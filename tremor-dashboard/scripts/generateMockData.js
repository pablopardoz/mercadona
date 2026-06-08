// Regenera src/data/mockData.js desde gastos.duckdb
// Uso: node scripts/generateMockData.js
// Requiere: duckdb CLI en PATH

import { execSync } from "child_process"
import { writeFileSync } from "fs"
import { resolve, dirname } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))
const DB = resolve(__dirname, "../../gastos.duckdb")

function query(sql) {
  const out = execSync(`duckdb "${DB}" -json -c "${sql.replace(/"/g, '\\"')}"`, {
    encoding: "utf-8",
  })
  return JSON.parse(out)
}

// 1. Resumen
const [resumen] = query(`SELECT COUNT(*) AS num_tickets, ROUND(SUM(total_gasto), 2) AS total_global FROM gastos.tickets`)

// 2. Por mes
const porMes = query(`SELECT strftime('%Y-%m', fecha) AS mes, ROUND(SUM(total_gasto), 2) AS total, COUNT(*) AS num_tickets FROM gastos.tickets GROUP BY mes ORDER BY mes`)

// 3. Por categoría
const porCategoria = query(`SELECT categoria, ROUND(SUM(precio_total), 2) AS total, COUNT(*) AS num_productos FROM gastos.lineas_ticket GROUP BY categoria ORDER BY total DESC`)

// 4. Total productos
const [{ totalProductos }] = query(`SELECT COUNT(*) AS totalProductos FROM gastos.lineas_ticket`)

// 5. Categorías distintas
const [{ categoriasDistintas }] = query(`SELECT COUNT(DISTINCT categoria) AS categoriasDistintas FROM gastos.lineas_ticket`)

// 6. Producto más caro
const [prodCaro] = query(`SELECT l.nombre_normalizado AS nombre, ROUND(l.precio_unitario, 2) AS precio FROM gastos.lineas_ticket l ORDER BY l.precio_unitario DESC LIMIT 1`)

// 7. Producto más frecuente
const [prodFrec] = query(`SELECT nombre_normalizado AS nombre, COUNT(DISTINCT ticket_hash) AS veces FROM gastos.lineas_ticket GROUP BY nombre_normalizado ORDER BY veces DESC LIMIT 1`)

// 8. Tickets con items
const ticketsRaw = query(`SELECT ticket_hash, supermercado, fecha, hora, ROUND(total_gasto, 2) AS total_gasto FROM gastos.tickets ORDER BY fecha DESC, hora DESC`)
const itemsRaw = query(`SELECT ticket_hash, nombre_normalizado AS producto, ROUND(precio_unitario, 2) AS precioUnitario, cantidad, ROUND(precio_total, 2) AS precioTotal, categoria, subcategoria FROM gastos.lineas_ticket ORDER BY ticket_hash, nombre_normalizado`)

const itemsByHash = {}
for (const item of itemsRaw) {
  if (!itemsByHash[item.ticket_hash]) itemsByHash[item.ticket_hash] = []
  itemsByHash[item.ticket_hash].push({
    producto: item.producto,
    precioUnitario: item.precioUnitario,
    cantidad: item.cantidad,
    precioTotal: item.precioTotal,
    categoria: item.categoria,
    subcategoria: item.subcategoria,
  })
}

const tickets = ticketsRaw.map((t) => ({
  id: t.ticket_hash.slice(0, 8),
  ticket_hash: t.ticket_hash,
  fecha: t.fecha,
  hora: t.hora,
  supermercado: t.supermercado,
  total: t.total_gasto,
  items: itemsByHash[t.ticket_hash] || [],
}))

// Calcular KPIs
const totalGastado = resumen.total_global
const numTickets = resumen.num_tickets
const ticketMedio = numTickets > 0 ? +(totalGastado / numTickets).toFixed(2) : 0
const gastoMedioProducto = totalProductos > 0 ? +(totalGastado / totalProductos).toFixed(2) : 0

// Calcular cambios (mes anterior vs actual)
let changeTotal = 0, changeTickets = 0, changeTicketMedio = 0
if (porMes.length >= 2) {
  const prev = porMes[porMes.length - 2]
  const curr = porMes[porMes.length - 1]
  changeTotal = prev.total > 0 ? +(((curr.total - prev.total) / prev.total) * 100).toFixed(1) : 0
  changeTickets = prev.num_tickets > 0 ? +(((curr.num_tickets - prev.num_tickets) / prev.num_tickets) * 100).toFixed(1) : 0
  const prevMedio = prev.total / prev.num_tickets
  const currMedio = curr.total / curr.num_tickets
  changeTicketMedio = prevMedio > 0 ? +(((currMedio - prevMedio) / prevMedio) * 100).toFixed(1) : 0
}

// Construir ventas mensuales
const meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
const ventasMensuales = porMes.map((p) => {
  const m = parseInt(p.mes.split("-")[1], 10)
  return { mes: meses[m - 1], ventas: p.total }
})

// Construir categorías para treemap
const totalCat = porCategoria.reduce((s, c) => s + c.total, 0)
const categoriasSupermercado = porCategoria.map((c) => ({
  name: c.categoria,
  value: c.total,
  porcentaje: totalCat > 0 ? +((c.total / totalCat) * 100).toFixed(1) : 0,
}))

// Generar contenido del archivo JS
const content = `// GENERATED FROM gastos.duckdb — DO NOT EDIT BY HAND
// Run \`npm run db:sync\` to regenerate

export const kpiData = {
  totalGastado: { value: ${totalGastado}, change: ${changeTotal}, changeType: ${changeTotal >= 0 ? '"positive"' : '"negative"'} },
  numTickets: { value: ${numTickets}, change: ${changeTickets}, changeType: ${changeTickets >= 0 ? '"positive"' : '"negative"'} },
  ticketMedio: { value: ${ticketMedio}, change: ${changeTicketMedio}, changeType: ${changeTicketMedio >= 0 ? '"positive"' : '"negative"'} },
  numProductos: { value: ${totalProductos}, change: 0, changeType: "positive" },
  categoriasDistintas: { value: ${categoriasDistintas}, change: 0, changeType: "positive" },
  productoCaro: { value: ${prodCaro.precio}, change: 0, changeType: "positive" },
  productoFrecuente: { value: ${prodFrec.veces}, change: 0, changeType: "positive" },
  gastoMedioProducto: { value: ${gastoMedioProducto}, change: 0, changeType: "positive" },
}

export const ventasMensuales = ${JSON.stringify(ventasMensuales, null, 2)}

export const categoriasSupermercado = ${JSON.stringify(categoriasSupermercado, null, 2)}

export const tickets = ${JSON.stringify(tickets, null, 2)}

export const menuItems = [
  { id: "dashboard", label: "Dashboard", icon: "LayoutDashboard" },
  { id: "ventas", label: "Ventas", icon: "TrendingUp" },
  { id: "productos", label: "Productos", icon: "Package" },
  { id: "clientes", label: "Clientes", icon: "Users" },
  { id: "informes", label: "Informes", icon: "FileText" },
  { id: "ajustes", label: "Ajustes", icon: "Settings" },
]
`

const outPath = resolve(__dirname, "../src/data/mockData.js")
writeFileSync(outPath, content, "utf-8")
console.log("✓ mockData.js regenerado desde", DB)
