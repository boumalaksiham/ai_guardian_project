import { useEffect, useState } from 'react'
import axios from 'axios'

export default function EventsPage() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = () => axios.get('/api/events/?limit=50')
      .then(r => setEvents(r.data))
      .catch(() => setEvents([]))
      .finally(() => setLoading(false))

    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Events</h1>
      <p style={{ color: '#64748b', marginBottom: 24, fontSize: 14 }}>All LLM interaction events</p>
      {loading ? <div style={{ color: '#64748b' }}>Loading...</div> :
       events.length === 0 ?
        <div className="card" style={{ color: '#64748b', textAlign: 'center', padding: 40 }}>No events yet.</div> :
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {events.map(e => (
            <div key={e.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ display: 'flex', gap: 8 }}>
                  <span className={`badge ${e.success ? 'badge-green' : 'badge-red'}`}>
                    {e.success ? '✓ success' : '✗ failed'}
                  </span>
                  <span className="badge badge-blue">{e.model_name}</span>
                </div>
                <span style={{ fontSize: 12, color: '#64748b' }}>{new Date(e.created_at).toLocaleString()}</span>
              </div>
              <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>
                <strong style={{ color: '#e2e8f0' }}>Prompt:</strong> {e.input_prompt?.slice(0, 120)}{e.input_prompt?.length > 120 ? '...' : ''}
              </div>
              <div style={{ display: 'flex', gap: 20, fontSize: 12, color: '#64748b' }}>
                {e.latency_ms && <span>⏱ {e.latency_ms}ms</span>}
                {e.total_tokens && <span>🔢 {e.total_tokens} tokens</span>}
                {e.cost_usd && <span>💰 ${e.cost_usd}</span>}
              </div>
            </div>
          ))}
        </div>
      }
    </div>
  )
}