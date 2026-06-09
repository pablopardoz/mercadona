import { Card, Title, Text } from "@tremor/react"
import { Treemap, ResponsiveContainer, Tooltip } from "recharts"

const colors = [
  "#2563eb",
  "#059669",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#db2777",
  "#0891b2",
  "#ea580c",
  "#4f46e5",
  "#ca8a04",
  "#16a34a",
  "#e11d48",
]

export default function TreemapChart({ data }) {
  const chartData = data.map((d, i) => ({
    ...d,
    fill: colors[i % colors.length],
  }))

  return (
    <Card>
      <Title>Distribución por Categoría</Title>
      <Text>Porcentaje de gasto por categoría de producto</Text>
      <div className="mt-4 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={chartData}
            dataKey="value"
            aspectRatio={4 / 3}
            stroke="#fff"
            content={<CustomTreemapContent chartColors={colors} />}
          >
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0].payload
                return (
                  <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-sm">
                    <p className="font-medium text-gray-900">{d.name}</p>
                    <p className="text-gray-600">{d.porcentaje}% del gasto</p>
                  </div>
                )
              }}
            />
          </Treemap>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1">
        {data.map((d, i) => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs text-gray-600">
            <div
              className="w-2.5 h-2.5 rounded-sm"
              style={{ backgroundColor: colors[i % colors.length] }}
            />
            {d.name} ({d.porcentaje}%)
          </div>
        ))}
      </div>
    </Card>
  )
}

function CustomTreemapContent({ root, depth, x, y, width, height, index, payload, chartColors }) {
  const color = payload?.fill || chartColors?.[index % chartColors.length] || "#6366f1"

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: color,
          stroke: "#fff",
          strokeWidth: 2,
          cursor: "pointer",
        }}
        rx={4}
      />
      {width > 50 && height > 30 && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2 - 6}
            textAnchor="middle"
            fill="#fff"
            fontSize={13}
            fontWeight={600}
          >
            {payload?.name}
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2 + 12}
            textAnchor="middle"
            fill="#ffffffcc"
            fontSize={11}
          >
            {payload?.porcentaje}%
          </text>
        </>
      )}
    </g>
  )
}
