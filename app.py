import os
import streamlit as st
import fitz  # PyMuPDF
import json
import pandas as pd
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Analizador de Tickets", layout="wide")
st.title("🛒 Analizador Inteligente de Tickets de Compra")

# --- TAXONOMÍA DE 3 NIVELES ---
TAXONOMIA = {
    "Alimentacion": {
        "Lacteos y Huevos": ["Leche", "Yogur", "Queso", "Huevos", "Mantequilla"],
        "Carnes y Pescados": ["Pollo", "Ternera", "Cerdo", "Pescado", "Marisco", "Embutidos"],
        "Frutas y Verduras": ["Fruta fresca", "Verdura fresca", "Congelados vegetales"],
        "Despensa": ["Pasta y Arroz", "Legumbres", "Conservas", "Salsas", "Aceites", "Panaderia", "Dulces"]
    },
    "Bebidas": {
        "Sin Alcohol": ["Agua", "Refrescos", "Zumos", "Bebidas vegetales"],
        "Con Alcohol": ["Cerveza", "Vino", "Licores"]
    },
    "Hogar y Limpieza": {
        "Limpieza": ["Detergente", "Suavizante", "Limpiasuelos", "Friegaplatos"],
        "Celulosa": ["Papel higienico", "Servilletas", "Rollo cocina"]
    },
    "Cuidado Personal": {
        "Higiene": ["Gel", "Champu", "Desodorante", "Pasta dental"],
        "Cosmetica": ["Cremas", "Maquillaje"]
    }
}

# --- FUNCIONES CORE ---
def extraer_texto_pdf(file_bytes):
    texto = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def procesar_ticket_con_ia(texto):
    """Envía el texto a Llama 3 usando la API Key hardcodeada."""
    
    # Comprobación de seguridad por si se te olvida ponerla
    if GROQ_API_KEY == "PON_TU_API_KEY_DE_GROQ_AQUI":
        st.error("⚠️ Por favor, pon tu API Key en la variable GROQ_API_KEY dentro del código.")
        return None

    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    Analiza este texto de un ticket de supermercado y extrae los datos.
    
    TAXONOMÍA ESTRICTA (Categoría -> Subcategoría -> Tipo):
    {json.dumps(TAXONOMIA, indent=2)}
    
    REGLAS:
    1. Clasifica cada producto usando EXCLUSIVAMENTE los nombres de la taxonomía anterior.
    2. Si algo no encaja perfectamente, usa "Otros" en los 3 niveles.
    3. Asegúrate de que las fechas sean formato YYYY-MM-DD.
    
    Texto del ticket:
    {texto}
    
    Devuelve UNICAMENTE un objeto JSON válido con esta estructura exacta:
    {{
      "supermercado": "Nombre del super",
      "direccion": "Direccion completa o Ciudad si no hay calle",
      "fecha": "YYYY-MM-DD",
      "total_ticket": 0.00,
      "productos": [
        {{
          "nombre": "Nombre original en el ticket",
          "precio": 0.00,
          "categoria": "Nivel 1",
          "subcategoria": "Nivel 2",
          "tipo": "Nivel 3"
        }}
      ]
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente experto en contabilidad. Tu única salida debe ser texto en formato JSON. No añadas introducciones ni saludos."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="qwen/qwen3-32b",
            temperature=0, 
            response_format={"type": "json_object"} 
        )
        
        respuesta_texto = chat_completion.choices[0].message.content
        return json.loads(respuesta_texto)
        
    except Exception as e:
        st.error(f"Error procesando con IA: {e}")
        return None

# --- UI DE STREAMLIT ---
with st.sidebar:
    st.header("⚙️ Sube tus archivos")
    # El campo de la API Key ha desaparecido de aquí
    uploaded_files = st.file_uploader("Selecciona los tickets en PDF", type="pdf", accept_multiple_files=True)

if "datos_procesados" not in st.session_state:
    st.session_state.datos_procesados = []

if uploaded_files:
    if st.button("Procesar Tickets"):
        with st.spinner('Analizando tickets con IA...'):
            nuevos_datos = []
            for file in uploaded_files:
                bytes_pdf = file.read()
                texto = extraer_texto_pdf(bytes_pdf)
                resultado = procesar_ticket_con_ia(texto)
                if resultado:
                    nuevos_datos.append(resultado)
            
            st.session_state.datos_procesados = nuevos_datos
            if nuevos_datos:
                st.success("¡Tickets procesados con éxito!")

# --- VISUALIZACIÓN DE DATOS ---
if st.session_state.datos_procesados:
    datos = st.session_state.datos_procesados
    
    df_tickets = pd.DataFrame([{
        "Supermercado": d["supermercado"],
        "Fecha": pd.to_datetime(d["fecha"]),
        "Total": d["total_ticket"],
        "Dirección": d["direccion"]
    } for d in datos])
    
    lista_productos = []
    for d in datos:
        for p in d["productos"]:
            p["Fecha"] = pd.to_datetime(d["fecha"])
            p["Supermercado"] = d["supermercado"]
            lista_productos.append(p)
    df_productos = pd.DataFrame(lista_productos)

    st.subheader("Resumen de Gastos")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total", f"€{df_tickets['Total'].sum():.2f}")
    col2.metric("Tickets Procesados", len(df_tickets))
    col3.metric("Coste Medio por Ticket", f"€{df_tickets['Total'].mean():.2f}")
    st.divider()

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("**Gasto Total por Fecha**")
        gasto_fecha = df_tickets.groupby("Fecha")["Total"].sum().reset_index()
        fig_line = px.bar(gasto_fecha, x="Fecha", y="Total", text="Total", template="plotly_white")
        fig_line.update_traces(texttemplate='%{text:.2f}€', textposition='outside')
        st.plotly_chart(fig_line, use_container_width=True)

    with col_graf2:
        st.markdown("**Gasto por Categoría (Nivel 1)**")
        gasto_cat = df_productos.groupby("categoria")["precio"].sum().reset_index()
        fig_pie = px.pie(gasto_cat, values='precio', names='categoria', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()
    
    st.markdown("**Desglose Profundo: Categoría > Subcategoría > Tipo**")
    st.caption("Haz clic en una categoría para profundizar.")
    df_jerarquia = df_productos.groupby(['categoria', 'subcategoria', 'tipo'])['precio'].sum().reset_index()
    df_jerarquia = df_jerarquia[df_jerarquia['precio'] > 0]
    
    fig_sunburst = px.sunburst(
        df_jerarquia, 
        path=['categoria', 'subcategoria', 'tipo'], 
        values='precio',
        color='precio',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)

    st.divider()

    with st.expander("Ver Datos Extraídos en Crudo"):
        st.write("**Tickets:**")
        st.dataframe(df_tickets)
        st.write("**Productos:**")
        st.dataframe(df_productos)