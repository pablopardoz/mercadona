import { useState, Fragment } from "react"
import { Card, Title, Text } from "@tremor/react"
import { ChevronDown, ChevronRight, Search, Receipt } from "lucide-react"
import ProductModal from "./ProductModal"

export default function TicketsTable({ tickets }) {
  const [expanded, setExpanded] = useState(null)
  const [search, setSearch] = useState("")
  const [modalItem, setModalItem] = useState(null)

  const filtered = tickets.filter(
    (t) =>
      t.id.toLowerCase().includes(search.toLowerCase()) ||
      t.fecha.includes(search)
  )

  return (
    <>
      <Card>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <Title>Tickets de Compra</Title>
            <Text>{tickets.length} tickets este mes</Text>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar ticket..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-48 lg:w-56"
            />
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <Th className="w-8" />
                <Th>Ticket</Th>
                <Th>Fecha</Th>
                <Th>Supermercado</Th>
                <Th className="text-right">Total</Th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((ticket) => {
                const isOpen = expanded === ticket.id
                return (
                  <Fragment key={ticket.id}>
                    <tr
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setExpanded(isOpen ? null : ticket.id)}
                    >
                      <td className="py-3 px-2">
                        {isOpen ? (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        )}
                      </td>
                      <td className="py-3 px-2 font-medium text-gray-900">
                        {ticket.id}
                      </td>
                      <td className="py-3 px-2 text-gray-700">
                        {new Date(ticket.fecha).toLocaleDateString("es-ES", {
                          day: "2-digit",
                          month: "2-digit",
                          year: "numeric",
                        })}
                      </td>
                      <td className="py-3 px-2">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 bg-orange-100 rounded flex items-center justify-center">
                            <span className="text-xs font-bold text-orange-600">M</span>
                          </div>
                          <span className="text-gray-700">{ticket.supermercado}</span>
                        </div>
                      </td>
                      <td className="py-3 px-2 text-right font-medium text-gray-900">
                        {ticket.total.toFixed(2)} €
                      </td>
                    </tr>
                    {isOpen && (
                      <tr key={`${ticket.id}-detail`}>
                        <td colSpan={5} className="bg-gray-50 p-0">
                          <div className="px-8 py-4">
                            <div className="flex items-center gap-2 mb-3">
                              <Receipt className="w-4 h-4 text-gray-400" />
                              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Productos
                              </span>
                            </div>
                            <table className="w-full text-sm">
                              <thead>
                                <tr className="border-b border-gray-200">
                                  <Th className="text-left">Producto</Th>
                                  <Th className="text-right">Precio Unit.</Th>
                                  <Th className="text-center">Cant.</Th>
                                  <Th className="text-right">Precio Total</Th>
                                </tr>
                              </thead>
                              <tbody>
                                {ticket.items.map((item, i) => (
                                  <tr key={i} className="border-b border-gray-100">
                                    <td className="py-2">
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation()
                                          setModalItem(item)
                                        }}
                                        className="text-blue-600 hover:text-blue-800 hover:underline text-left transition-colors"
                                      >
                                        {item.producto}
                                      </button>
                                    </td>
                                    <td className="py-2 text-right text-gray-600">
                                      {item.precioUnitario.toFixed(2)} €
                                    </td>
                                    <td className="py-2 text-center text-gray-600">
                                      {item.cantidad}
                                    </td>
                                    <td className="py-2 text-right font-medium text-gray-900">
                                      {item.precioTotal.toFixed(2)} €
                                    </td>
                                  </tr>
                                ))}
                                <tr className="font-semibold">
                                  <td colSpan={3} className="py-2 text-right text-gray-700">
                                    Total Ticket
                                  </td>
                                  <td className="py-2 text-right text-gray-900">
                                    {ticket.total.toFixed(2)} €
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <ProductModal
        open={!!modalItem}
        item={modalItem}
        onClose={() => setModalItem(null)}
      />
    </>
  )
}

function Th({ children, className = "" }) {
  return (
    <th className={`py-3 px-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${className}`}>
      {children}
    </th>
  )
}
