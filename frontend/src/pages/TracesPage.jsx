import { useEffect, useState } from 'react'
import axios from 'axios'

export default function TracesPage() {
  const [traces, setTraces] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = () => axios.get('/api/traces/')
      .then(r => setTraces(r.data))
      .catch(() => setTraces([]))
      .finally(() => setLoading(false))

    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Traces</h1>
      <p style={{ color: '#64748b', marginBottom: 24, fontSize: 14 }}>Multi-step request flows</p>
      {loading ? <div style={{ color: '#64748b' }}>Loading...</div> :
       traces.length === 0 ?
        <div className="card" style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>
          No traces yet. Use <code style={{ color: '#6366f1' }}>start_trace()</code> in the SDK.
        </div> :
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {traces.map(t => (
            <div key={t.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span style={{ fontWeight: 600, color: '#6366f1' }}>🔍 {t.trace_id?.slice(0, 16)}...</span>
                <span className={`badge ${t.success ? 'badge-green' : 'badge-red'}`}>{t.success ? 'success' : 'failed'}</span>
              </div>
              <div style={{ display: 'flex', gap: 24, fontSize: 13, color: '#94a3b8' }}>
                {t.total_latency_ms && <span>⏱ {t.total_latency_ms}ms</span>}
                {t.total_cost_usd && <span>💰 ${t.total_cost_usd}</span>}
                {t.step_count && <span>📋 {t.step_count} steps</span>}
              </div>
            </div>
          ))}
        </div>
      }
    </div>
  )
}