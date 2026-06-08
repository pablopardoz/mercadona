# DashPro — Dashboard de Tickets de Supermercado

## Stack

- **Vite** + **React 19**
- **Tremor** (componentes de UI: Card, Title, Text, Badge, Metric)
- **Recharts** (gráficos: BarChart, Treemap)
- **Tailwind CSS 3**
- **Lucide React** (iconos)

## Estructura del Proyecto

```
tremor-dashboard/
├── index.html
├── tailwind.config.js          # Config Tailwind + tema Tremor
├── postcss.config.js
├── src/
│   ├── main.jsx                # Entry point
│   ├── index.css               # Directivas Tailwind
│   ├── App.jsx                 # Layout principal (sidebar + contenido)
│   ├── data/
│   │   └── mockData.js         # Todos los datos mock del dashboard
│   └── components/
│       ├── Sidebar.jsx         # Panel lateral izquierdo (responsive)
│       ├── KpiCards.jsx        # Tarjetas de KPIs (8 indicadores)
│       ├── MonthlyBarChart.jsx # Gráfico de barras verticales mensuales
│       ├── TreemapChart.jsx    # Treemap de categorías de supermercado
│       ├── TicketsTable.jsx    # Tabla de tickets con filas expandibles
│       └── ProductModal.jsx    # Modal para editar producto del ticket
```

## Componentes y Funcionamiento

### App.jsx
- Layout de dos columnas: sidebar fijo + contenido principal.
- Estado `active` para navegación, `sidebarOpen` para menú hamburguesa en móvil.
- Distribuye los datos mock a los componentes hijos.

### Sidebar
- Menú vertical con 6 secciones (Dashboard, Ventas, Productos, Clientes, Informes, Ajustes).
- En móvil se oculta y se abre como overlay con fondo semitransparente.
- El logo y la información del usuario están al final.

### KpiCards
- 8 tarjetas en grid responsive (1 col móvil, 2 tablet, 4 desktop).
- Cada KPI muestra: título, valor formateado, icono, badge de cambio vs mes anterior.
- Los cambios positivos se muestran en verde, negativos en rojo.

### MonthlyBarChart
- Gráfico Recharts `BarChart` con barras verticales.
- Eje X: meses (Ene-Dic). Eje Y: ventas en dólares.
- Tooltip personalizado con formato moneda.

### TreemapChart
- Gráfico Recharts `Treemap` con rectángulos anidados.
- Muestra 8 categorías de supermercado (Carne, Pescado, Lácteos...).
- Cada rectángulo muestra nombre y porcentaje.
- Tooltip con nombre y porcentaje. Leyenda inferior con colores.

### TicketsTable
- Tabla con tickets de compra (solo Mercadona).
- Búsqueda por ID de ticket o fecha.
- Cada fila es expandible: al hacer clic se despliega la lista de productos del ticket.
- Los nombres de producto son botones que abren `ProductModal`.

### ProductModal
- Modal superpuesto al hacer clic en un producto.
- Muestra: nombre (solo lectura), precio unitario (input), categoría (select), subcategoría (select).
- El select de subcategoría se filtra según la categoría elegida.
- Botón Cancelar funcional. Botón Guardar deshabilitado (listo para implementar lógica de guardado).

## Datos Mock

Todos los datos están en `src/data/mockData.js`:
- `kpiData`: 8 indicadores con valor, cambio y tipo de cambio
- `ventasMensuales`: 12 meses con ventas
- `categoriasSupermercado`: 8 categorías con valor y porcentaje
- `tickets`: 10 tickets con items que incluyen producto, precio, cantidad, categoría y subcategoría

## Responsive Design

- Sidebar: oculto en móvil (< 1024px), se abre con botón hamburguesa
- KPIs: 1 col móvil → 2 col tablet → 4 col desktop
- Gráficos: 1 col móvil/tablet → 2 col desktop
- Tabla: scroll horizontal en móvil, columnas adaptativas
- Modal: centrado, overlay semitransparente, padding adaptable

## Para empezar

```bash
npm install --legacy-peer-deps
npm run dev
```

## Para construir

```bash
npm run build
npm run preview
```
