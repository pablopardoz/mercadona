import { useState, useEffect, useMemo } from "react"
import { Search, ArrowLeft, Package, TrendingUp, DollarSign, BarChart3 } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { fetchProductos, fetchProductoCompras } from "../services/api"

const supermarketPalette = {
  Mercadona: "#2563eb",
  Carrefour: "#dc2626",
  Aldi: "#f59e0b",
  Lidl: "#16a34a",
  Dia: "#0891b2",
  Alcampo: "#7c3aed",
  Consum: "#db2777",
  default: "#6b7280",
}

function formatDate(dateStr) {
  const d = new Date(dateStr + "T12:00:00")
  return d.toLocaleDateString("es-ES", { day: "numeric", month: "short" })
}

function MetricCard({ icon: Icon, label, value, format }) {
  const display = format === "currency" ? `${Number(value).toFixed(2)} €` : value
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
      <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
        <Icon className="w-5 h-5 text-blue-600" />
      </div>
      <div>
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{label}</p>
        <p className="text-xl font-semibold text-gray-900">{display}</p>
      </div>
    </div>
  )
}

export default function ProductosTab() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("")
  const [selected, setSelected] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    fetchProductos()
      .then(setProducts)
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    if (!filter) return products
    const q = filter.toLowerCase()
    return products.filter(p => p.producto.toLowerCase().includes(q))
  }, [products, filter])

  useEffect(() => {
    if (!selected) { setDetail(null); return }
    setDetailLoading(true)
    fetchProductoCompras(selected.producto)
      .then(data => {
        const year = new Date().getFullYear().toString()
        const thisYear = data.filter(p => p.fecha.startsWith(year))
        const prices = data.map(p => p.precioUnitario)
        const supermarketSet = [...new Set(data.map(p => p.supermercado))]
        const chartDates = [...new Set(thisYear.map(p => p.fecha))].sort()
        const chartData = chartDates.map(date => {
          const point = { fecha: formatDate(date) }
          supermarketSet.forEach(sm => {
            const match = thisYear.find(p => p.fecha === date && p.supermercado === sm)
            point[sm] = match ? match.precioUnitario : null
          })
          return point
        })
        setDetail({
          vecesComprado: data.length,
          precioMedio: prices.reduce((s, p) => s + p, 0) / prices.length,
          precioMax: Math.max(...prices),
          precioMin: Math.min(...prices),
          chartData,
          supermarkets: supermarketSet,
        })
        setDetailLoading(false)
      })
  }, [selected])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex flex-col items-center gap-2">
          <Package className="w-8 h-8 text-blue-600 animate-pulse" />
          <span className="text-gray-500 text-sm">Cargando productos...</span>
        </div>
      </div>
    )
  }

  if (selected && detail) {
    return (
      <div className="space-y-6">
        <button onClick={() => setSelected(null)} className="inline-flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Volver a productos
        </button>

        <h2 className="text-lg font-semibold text-gray-900">{selected.producto}</h2>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard icon={TrendingUp} label="Veces comprado" value={detail.vecesComprado} />
          <MetricCard icon={DollarSign} label="Precio medio" value={detail.precioMedio} format="currency" />
          <MetricCard icon={BarChart3} label="Precio máximo" value={detail.precioMax} format="currency" />
          <MetricCard icon={BarChart3} label="Precio mínimo" value={detail.precioMin} format="currency" />
        </div>

        {detail.chartData.length > 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Evolución de precio este año</h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={detail.chartData} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="fecha" tick={{ fontSize: 12 }} stroke="#9ca3af" />
                <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" tickFormatter={v => `${v}€`} />
                <Tooltip formatter={v => [`${Number(v).toFixed(2)} €`, "Precio"]} labelFormatter={l => `Fecha: ${l}`} />
                <Legend />
                {detail.supermarkets.map(sm => (
                  <Line key={sm} type="monotone" dataKey={sm} name={sm} stroke={supermarketPalette[sm] || supermarketPalette.default} strokeWidth={2} dot={{ r: 4 }} connectNulls />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <Package className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No hay compras de este producto en {new Date().getFullYear()}</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar producto..."
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
        />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {filtered.length === 0 ? (
          <div className="py-12 text-center">
            <Package className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No se encontraron productos</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
            {filtered.map(p => (
              <li key={p.producto}>
                <button
                  onClick={() => setSelected(p)}
                  className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors text-left"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{p.producto}</p>
                    <p className="text-xs text-gray-500">{p.categoria}</p>
                  </div>
                  <div className="text-right shrink-0 ml-4">
                    <p className="text-sm font-semibold text-gray-900">{p.veces}x</p>
                    <p className="text-xs text-gray-400">comprado</p>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}