import { useEffect, useState } from 'react'
import axios from 'axios'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = () => axios.get('/api/alerts/?resolved=false')
      .then(r => setAlerts(r.data))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false))

    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [])

  const resolve = (id) => axios.patch(`/api/alerts/${id}/resolve`)
    .then(() => setAlerts(prev => prev.filter(a => a.id !== id)))

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Alerts</h1>
      <p style={{ color: '#64748b', marginBottom: 24, fontSize: 14 }}>Active threshold violations</p>
      {loading ? <div style={{ color: '#64748b' }}>Loading...</div> :
       alerts.length === 0 ?
        <div className="card" style={{ color: '#10b981', textAlign: 'center', padding: 40 }}>✅ No active alerts</div> :
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {alerts.map(a => (
            <div key={a.id} className="card" style={{
              borderLeft: `3px solid ${a.severity === 'critical' ? '#ef4444' : '#f59e0b'}`,
              display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'
            }}>
              <div>
                <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
                  <span className={`badge ${a.severity === 'critical' ? 'badge-red' : 'badge-yellow'}`}>{a.severity}</span>
                  <span className="badge badge-blue">{a.alert_type}</span>
                </div>
                <div style={{ fontSize: 14 }}>{a.message}</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{new Date(a.created_at).toLocaleString()}</div>
              </div>
              <button onClick={() => resolve(a.id)} style={{
                background: 'rgba(16,185,129,0.1)', border: '1px solid #10b981',
                color: '#10b981', padding: '6px 14px', borderRadius: 6, cursor: 'pointer', fontSize: 12
              }}>Resolve</button>
            </div>
          ))}
        </div>
      }
    </div>
  )
}