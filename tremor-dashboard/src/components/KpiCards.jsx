import { Card, Text, Metric, Flex, Badge } from "@tremor/react"
import {
  Euro,
  ShoppingCart,
  Receipt,
  Package,
  Layers,
  Crown,
  Repeat,
  TrendingUp,
} from "lucide-react"

const kpiConfig = [
  { key: "totalGastado", title: "Total Gastado", icon: Euro },
  { key: "numTickets", title: "Tickets", icon: ShoppingCart },
  { key: "ticketMedio", title: "Ticket Medio", icon: Receipt },
  { key: "numProductos", title: "Productos", icon: Package },
  { key: "categoriasDistintas", title: "Categorías", icon: Layers },
  { key: "productoCaro", title: "Prod. Más Caro", icon: Crown },
  { key: "productoFrecuente", title: "Prod. + Frecuente (veces)", icon: Repeat },
  { key: "gastoMedioProducto", title: "Gasto Medio/Prod.", icon: TrendingUp },
]

function formatValue(value, key) {
  const num = Number(value)
  switch (key) {
    case "totalGastado":
    case "ticketMedio":
    case "gastoMedioProducto":
    case "productoCaro":
      return `${num.toFixed(2)} €`
    case "numTickets":
    case "numProductos":
    case "categoriasDistintas":
    case "productoFrecuente":
      return num.toLocaleString("es-ES")
    default:
      return num.toLocaleString("es-ES")
  }
}

export default function KpiCards({ data }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      {kpiConfig.map((kpi) => {
        const item = data[kpi.key]
        const Icon = kpi.icon
        const isPositive = item.changeType === "positive"
        const hasChange = item.change !== 0
        return (
          <Card key={kpi.key} className="relative overflow-hidden">
            <Flex alignItems="start" justifyContent="between">
              <div>
                <Text className="text-gray-500">{kpi.title}</Text>
                <Metric className="mt-1 text-gray-900">
                  {formatValue(item.value, kpi.key)}
                </Metric>
              </div>
              <div className="p-2 bg-blue-50 rounded-lg">
                <Icon className="w-5 h-5 text-blue-600" />
              </div>
            </Flex>
            {hasChange && (
              <Flex className="mt-3" alignItems="center" justifyContent="start">
                <Badge color={isPositive ? "emerald" : "red"} size="xs">
                  {isPositive ? "+" : ""}
                  {item.change}%
                </Badge>
                <Text className="ml-2 text-gray-500">vs mes anterior</Text>
              </Flex>
            )}
          </Card>
        )
      })}
    </div>
  )
}
