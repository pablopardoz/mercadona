import {
  LayoutDashboard, Receipt, Package, FileText, Settings, X, Users,
} from "lucide-react"

const menuItems = [
  { id: "dashboard", label: "Dashboard", icon: "LayoutDashboard" },
  { id: "tickets", label: "Tickets", icon: "Receipt" },
  { id: "productos", label: "Productos", icon: "Package" },
  { id: "informes", label: "Informes", icon: "FileText" },
  { id: "ajustes", label: "Ajustes", icon: "Settings" },
]

const iconMap = {
  LayoutDashboard, Receipt, Package, FileText, Settings,
}

export default function Sidebar({ active, setActive, open, setOpen }) {
  return (
    <>
      {open && <div className="fixed inset-0 bg-black/50 z-20 lg:hidden" onClick={() => setOpen(false)} />}
      <aside className={`fixed lg:sticky top-0 left-0 z-30 h-screen bg-white border-r border-gray-200 transition-all duration-300 ease-in-out ${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 lg:w-64`}>
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg text-gray-900">Gastos</span>
          </div>
          <button onClick={() => setOpen(false)} className="p-1 rounded-lg hover:bg-gray-100 lg:hidden">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = iconMap[item.icon]
            const isActive = active === item.id
            return (
              <button key={item.id} onClick={() => { setActive(item.id); setOpen(false) }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 ${isActive ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"}`}>
                <Icon className="w-5 h-5" /> {item.label}
              </button>
            )
          })}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <Users className="w-4 h-4 text-gray-500" />
            </div>
            <div className="text-sm">
              <p className="font-medium text-gray-900">Pablo</p>
              <p className="text-gray-500 text-xs">pablo@mercadona.es</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
