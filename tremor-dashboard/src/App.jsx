import { useState, useEffect } from "react"
import { Menu, AlertCircle, Loader2 } from "lucide-react"
import Sidebar from "./components/Sidebar"
import KpiCards from "./components/KpiCards"
import TreemapChart from "./components/TreemapChart"
import MonthlyBarChart from "./components/MonthlyBarChart"
import TicketsTable from "./components/TicketsTable"
import { fetchAllDashboardData } from "./services/api"

export default function App() {
  const [active, setActive] = useState("dashboard")
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAllDashboardData()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar
        active={active}
        setActive={setActive}
        open={sidebarOpen}
        setOpen={setSidebarOpen}
      />

      <main className="flex-1 min-w-0">
        <header className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 lg:px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                className="p-2 rounded-lg hover:bg-gray-100 lg:hidden"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                {active === "dashboard" ? "Dashboard" : active.charAt(0).toUpperCase() + active.slice(1)}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500 hidden sm:block">
                {new Date().toLocaleDateString("es-ES", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </span>
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                P
              </div>
            </div>
          </div>
        </header>

        <div className="p-4 lg:p-6 space-y-6">
          {loading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              <span className="ml-3 text-gray-500">Cargando datos...</span>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center py-20">
              <div className="bg-red-50 border border-red-200 rounded-lg px-6 py-4 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <span className="text-red-700">Error al cargar datos: {error}</span>
              </div>
            </div>
          )}

          {data && (
            <>
              <KpiCards data={data.kpiData} />
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <MonthlyBarChart data={data.ventasMensuales} />
                <TreemapChart data={data.categoriasSupermercado} />
              </div>
              <TicketsTable tickets={data.tickets} />
            </>
          )}
        </div>
      </main>
    </div>
  )
}
