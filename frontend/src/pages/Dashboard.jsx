import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import axios from 'axios'

function StatCard({ label, value, color = '#6366f1' }) {
  return (
    <div className="card" style={{ flex: 1, minWidth: 160 }}>
      <div style={{ fontSize: 13, color: '#64748b', marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color }}>{value ?? '—'}</div>
    </div>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [latency, setLatency] = useState([])
  const [costByModel, setCostByModel] = useState([])

  useEffect(() => {
    const load = () => Promise.all([
      axios.get('/api/metrics/summary'),
      axios.get('/api/metrics/latency-trend'),
      axios.get('/api/metrics/cost-by-model'),
    ]).then(([s, l, c]) => {
      setSummary(s.data)
      setLatency(l.data.slice(0, 30).reverse())
      setCostByModel(c.data)
    }).catch(() => setSummary({
      total_requests: 0, success_rate: 0, avg_latency_ms: 0,
      total_cost_usd: 0, total_tokens: 0, active_alerts: 0
    }))

    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>Dashboard</h1>
      <p style={{ color: '#64748b', marginBottom: 24, fontSize: 14 }}>LLM observability overview · refreshes every 10 seconds</p>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 28 }}>
        <StatCard label="Total Requests" value={summary?.total_requests?.toLocaleString()} />
        <StatCard label="Success Rate" value={`${summary?.success_rate}%`} color={summary?.success_rate > 90 ? '#10b981' : '#ef4444'} />
        <StatCard label="Avg Latency" value={`${summary?.avg_latency_ms}ms`} color="#f59e0b" />
        <StatCard label="Total Cost" value={`$${summary?.total_cost_usd}`} color="#10b981" />
        <StatCard label="Total Tokens" value={summary?.total_tokens?.toLocaleString()} />
        <StatCard label="Active Alerts" value={summary?.active_alerts} color={summary?.active_alerts > 0 ? '#ef4444' : '#10b981'} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <div style={{ fontWeight: 600, marginBottom: 16 }}>Latency Trend</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={latency}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3148" />
              <XAxis dataKey="timestamp" hide />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3148' }} />
              <Line type="monotone" dataKey="latency_ms" stroke="#6366f1" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div style={{ fontWeight: 600, marginBottom: 16 }}>Cost by Model</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={costByModel}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3148" />
              <XAxis dataKey="model" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ background: '#1a1d27', border: '1px solid #2d3148' }} />
              <Bar dataKey="total_cost_usd" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}