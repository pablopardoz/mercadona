# Conexión con Datos Reales

## Fuentes de Datos

Todas las data mock están en `src/data/mockData.js`. Para conectar datos reales, sustituye las exportaciones por llamadas a tu API o base de datos.

---

### 1. KPIs (`kpiData`)

```js
// Reemplazar por llamada a API
export const kpiData = {
  ingresos: { value: 284500, change: 12.5, changeType: "positive" },
  pedidos: { value: 3890, change: -3.2, changeType: "negative" },
  ticketMedio: { value: 73.14, change: 5.8, changeType: "positive" },
  productosVendidos: { value: 28420, change: 9.1, changeType: "positive" },
  clientes: { value: 18420, change: 8.3, changeType: "positive" },
  devoluciones: { value: 287, change: -2.4, changeType: "positive" },
  margen: { value: 32.5, change: 1.2, changeType: "positive" },
  conversion: { value: 3.42, change: 1.1, changeType: "positive" },
}
```

**Formato esperado:** objeto con 8 claves. Cada valor tiene:
- `value` (number) — valor actual
- `change` (number) — variación porcentual
- `changeType` ("positive" | "negative") — determina el color del badge

**Api real:**

```js
export async function fetchKpiData() {
  const res = await fetch("/api/dashboard/kpis")
  return res.json()
}
```

**Importar en App.jsx con useEffect:**

```js
import { useState, useEffect } from "react"

const [kpiData, setKpiData] = useState(null)

useEffect(() => {
  fetchKpiData().then(setKpiData)
}, [])
```

---

### 2. Ventas Mensuales (`ventasMensuales`)

```js
// Formato esperado: array de { mes, ventas }
export const ventasMensuales = [
  { mes: "Ene", ventas: 21000 },
  ...
]
```

El componente `MonthlyBarChart` espera `dataKey="ventas"` en el eje Y y `dataKey="mes"` en el eje X.

---

### 3. Categorías para Treemap (`categoriasSupermercado`)

```js
// Formato esperado: array de { name, value, porcentaje }
export const categoriasSupermercado = [
  { name: "Carne", value: 28, porcentaje: 28 },
  ...
]
```

- `name` (string) — nombre de la categoría
- `value` (number) — valor absoluto para el tamaño del cuadrado
- `porcentaje` (number) — porcentaje que se muestra en el tooltip y leyenda

---

### 4. Tickets (`tickets`)

```js
// Formato esperado:
export const tickets = [
  {
    id: "TKT-001",
    fecha: "2026-06-07",           // string ISO o timestamp
    supermercado: "Mercadona",      // string
    total: 87.45,                   // number
    items: [
      {
        producto: "Solomillo de cerdo 500g",
        precioUnitario: 6.95,
        cantidad: 1,
        precioTotal: 6.95,
        categoria: "Carne",         // string — opcional, usado en el modal
        subcategoria: "Cerdo",      // string — opcional, usado en el modal
      },
    ],
  },
]
```

---

### 5. Categorías y subcategorías (modal)

```js
export const categorias = [
  { value: "Carne", subcategorias: ["Cerdo", "Pollo", "Ternera", "Cordero"] },
  ...
]
```

Se usan en `ProductModal.jsx` para los selects de categoría/subcategoría. Si tus categorías vienen de BD, cárgalas desde API.

---

### 6. Habilitar el botón Guardar

En `ProductModal.jsx`, el botón Guardar está así:

```jsx
<button disabled className="opacity-50 cursor-not-allowed">
```

Para habilitarlo:
1. Quitar `disabled`
2. Añadir `onClick` que llame a tu API:
```jsx
async function handleSave() {
  await fetch(`/api/productos/${item.id}`, {
    method: "PUT",
    body: JSON.stringify(form),
  })
  onClose()
}
```

---

### 7. Menú de navegación

```js
export const menuItems = [
  { id: "dashboard", label: "Dashboard", icon: "LayoutDashboard" },
  ...
]
```

Los iconos se resuelven con `iconMap` en `Sidebar.jsx`. Si añades más secciones, añade el icono correspondiente de `lucide-react`.

---

### Resumen de componentes y sus props

| Componente         | Props                              | Descripción                          |
|--------------------|------------------------------------|--------------------------------------|
| `Sidebar`          | `active, setActive, open, setOpen` | Navegación lateral                   |
| `KpiCards`         | `data`                             | Array de 8 KPIs                      |
| `MonthlyBarChart`  | `data`                             | Barras verticales por mes            |
| `TreemapChart`     | `data`                             | Treemap de categorías                |
| `TicketsTable`     | `tickets`                          | Tabla expandible de tickets          |
| `ProductModal`     | `open, item, onClose`              | Modal edición de producto            |
