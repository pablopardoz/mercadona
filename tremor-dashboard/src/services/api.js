const API_BASE = 'http://localhost:5000/api'

let _token = localStorage.getItem('token')

export function setToken(token) {
  _token = token
  if (token) localStorage.setItem('token', token)
  else localStorage.removeItem('token')
}

export function getToken() {
  return _token
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (_token) headers['Authorization'] = `Bearer ${_token}`
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(err.error || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function login(username, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  setToken(data.token)
  return data.token
}

export async function fetchKpis() {
  const [kpis, totals, categories] = await Promise.all([
    request('/kpis/'),
    request('/stats/totals'),
    request('/stats/categories'),
  ])

  const resumen = totals.resumen || {}
  const porMes = totals.por_mes || []
  const totalGastado = resumen.total_global || 0
  const numTickets = resumen.num_tickets || 0
  const ticketMedio = numTickets ? totalGastado / numTickets : 0

  const categorias = categories.por_categoria || []
  const numProductos = categorias.reduce((s, c) => s + (c.num_productos || 0), 0)
  const categoriasDistintas = categorias.length

  const productoCaro = kpis.producto_mas_caro
  const productoFrecuente = kpis.producto_mas_frecuente

  const totalProductos = numProductos || 1
  const gastoMedioProducto = totalGastado / totalProductos

  function computeChange(current, key) {
    if (porMes.length < 2) return { change: 0, changeType: 'positive' }
    const last = porMes[porMes.length - 1]
    const prev = porMes[porMes.length - 2]
    const currentVal = key === 'totalGastado' ? last.total : key === 'numTickets' ? last.num_tickets : 0
    const prevVal = key === 'totalGastado' ? prev.total : key === 'numTickets' ? prev.num_tickets : 0
    if (!prevVal) return { change: 0, changeType: 'positive' }
    const change = ((currentVal - prevVal) / prevVal) * 100
    return { change: Math.round(change * 10) / 10, changeType: change >= 0 ? 'positive' : 'negative' }
  }

  return {
    totalGastado: { value: totalGastado, ...computeChange(totalGastado, 'totalGastado') },
    numTickets: { value: numTickets, ...computeChange(numTickets, 'numTickets') },
    ticketMedio: { value: Math.round(ticketMedio * 100) / 100, change: 0, changeType: 'positive' },
    numProductos: { value: numProductos, change: 0, changeType: 'positive' },
    categoriasDistintas: { value: categoriasDistintas, change: 0, changeType: 'positive' },
    productoCaro: { value: productoCaro?.precio_unitario || 0, change: 0, changeType: 'positive' },
    productoFrecuente: { value: productoFrecuente?.veces || 0, change: 0, changeType: 'positive' },
    gastoMedioProducto: { value: Math.round(gastoMedioProducto * 100) / 100, change: 0, changeType: 'positive' },
  }
}

export async function fetchMonthlyStats() {
  const data = await request('/stats/totals')
  const porMes = data.por_mes || []
  const meses = { '01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic' }
  return porMes.map((m) => ({
    mes: meses[m.mes?.slice(-2)] || m.mes,
    ventas: Number(m.total) || 0,
  }))
}

export async function fetchCategories() {
  const data = await request('/stats/categories')
  const categorias = data.por_categoria || []
  const total = categorias.reduce((s, c) => s + (c.total || 0), 0)
  return categorias.map((c) => ({
    name: c.categoria,
    value: Number(c.total) || 0,
    porcentaje: total ? Math.round((c.total / total) * 1000) / 10 : 0,
  }))
}

export async function fetchTickets() {
  const data = await request('/tickets/')
  const tickets = data.tickets || []
  const detailPromises = tickets.map((t) =>
    request(`/tickets/${t.ticket_hash}`).catch(() => null)
  )
  const details = await Promise.all(detailPromises)
  return tickets.map((t, i) => {
    const detail = details[i]
    const lineas = detail?.lineas || []
    return {
      id: t.ticket_hash?.slice(0, 8),
      ticket_hash: t.ticket_hash,
      fecha: t.fecha,
      hora: t.hora || '',
      supermercado: t.supermercado,
      total: Number(t.total_gasto) || 0,
      items: lineas.map((l) => ({
        producto: l.nombre_normalizado,
        precioUnitario: Number(l.precio_unitario) || 0,
        cantidad: Number(l.cantidad) || 1,
        precioTotal: Number(l.precio_total) || 0,
        categoria: l.categoria || '',
        subcategoria: l.subcategoria || '',
      })),
    }
  })
}

export async function fetchAllDashboardData() {
  await login('pablo', 'pablo')
  const [kpiData, ventasMensuales, categoriasSupermercado, tickets] = await Promise.all([
    fetchKpis(),
    fetchMonthlyStats(),
    fetchCategories(),
    fetchTickets(),
  ])
  return { kpiData, ventasMensuales, categoriasSupermercado, tickets }
}
