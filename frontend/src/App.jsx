import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import EventsPage from './pages/EventsPage'
import AlertsPage from './pages/AlertsPage'
import TracesPage from './pages/TracesPage'

const NAV = [
  { id: 'dashboard', label: '⚡ Dashboard' },
  { id: 'events',    label: '📋 Events' },
  { id: 'alerts',    label: '🚨 Alerts' },
  { id: 'traces',    label: '🔍 Traces' },
]

export default function App() {
  const [page, setPage] = useState('dashboard')

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <nav style={{
        width: 220, background: '#13151f', borderRight: '1px solid #2d3148',
        padding: '24px 0', display: 'flex', flexDirection: 'column', gap: 4, flexShrink: 0
      }}>
        <div style={{ padding: '0 20px 24px', borderBottom: '1px solid #2d3148', marginBottom: 8 }}>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#6366f1' }}>🛡️ AI Guardian</div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>LLM Observability</div>
        </div>
        {NAV.map(n => (
          <button key={n.id} onClick={() => setPage(n.id)} style={{
            background: page === n.id ? 'rgba(99,102,241,0.15)' : 'transparent',
            border: 'none', color: page === n.id ? '#6366f1' : '#94a3b8',
            padding: '10px 20px', textAlign: 'left', cursor: 'pointer',
            fontSize: 14, fontWeight: page === n.id ? 600 : 400,
            borderLeft: page === n.id ? '3px solid #6366f1' : '3px solid transparent',
          }}>
            {n.label}
          </button>
        ))}
      </nav>
      <main style={{ flex: 1, padding: 28, overflowY: 'auto' }}>
        {page === 'dashboard' && <Dashboard />}
        {page === 'events'    && <EventsPage />}
        {page === 'alerts'    && <AlertsPage />}
        {page === 'traces'    && <TracesPage />}
      </main>
    </div>
  )
}