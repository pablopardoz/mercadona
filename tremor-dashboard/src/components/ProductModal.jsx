import { useState, useEffect } from "react"
import { X, Save } from "lucide-react"

const categorias = [
  { value: "Carne", subcategorias: ["Cerdo", "Pollo", "Ternera", "Cordero"] },
  { value: "Pescado", subcategorias: ["Pescado blanco", "Pescado azul", "Marisco"] },
  { value: "Lácteos", subcategorias: ["Leche", "Yogur", "Queso", "Mantequilla", "Huevos", "Aceite"] },
  { value: "Fruta y Verdura", subcategorias: ["Fruta", "Verdura"] },
  { value: "Panadería", subcategorias: ["Pan", "Bollería", "Cereales"] },
  { value: "Congelados", subcategorias: ["Pizza", "Verduras", "Helados", "Pescado"] },
  { value: "Bebidas", subcategorias: ["Agua", "Refrescos", "Zumo", "Cerveza", "Vino"] },
  { value: "Limpieza", subcategorias: ["Detergente", "Lavavajillas", "Lejía", "Papel"] },
]

export default function ProductModal({ open, item, onClose }) {
  const [form, setForm] = useState({
    precio: "",
    categoria: "",
    subcategoria: "",
  })

  useEffect(() => {
    if (item) {
      setForm({
        precio: item.precioUnitario.toString(),
        categoria: item.categoria || "",
        subcategoria: item.subcategoria || "",
      })
    }
  }, [item])

  const subcategorias = categorias.find((c) => c.value === form.categoria)?.subcategorias || []

  if (!open || !item) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-lg z-10">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Editar Producto</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Producto
            </label>
            <p className="text-sm text-gray-900 bg-gray-50 rounded-lg px-3 py-2 border border-gray-200">
              {item.producto}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Precio Unitario (€)
            </label>
            <input
              type="number"
              step="0.01"
              value={form.precio}
              onChange={(e) => setForm({ ...form, precio: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoría
            </label>
            <select
              value={form.categoria}
              onChange={(e) =>
                setForm({ categoria: e.target.value, subcategoria: "" })
              }
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Seleccionar categoría</option>
              {categorias.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.value}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subcategoría
            </label>
            <select
              value={form.subcategoria}
              onChange={(e) => setForm({ ...form, subcategoria: e.target.value })}
              disabled={!form.categoria}
              className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-400"
            >
              <option value="">Seleccionar subcategoría</option>
              {subcategorias.map((sub) => (
                <option key={sub} value={sub}>
                  {sub}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            disabled
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg opacity-50 cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            Guardar
          </button>
        </div>
      </div>
    </div>
  )
}
