import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getDashboard } from '../api'
import { useAuth } from '../contexts/AuthContext'
import './Dashboard.css'

function fmtCurrency(n) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(n)
}

export default function Dashboard() {
    const { user } = useAuth()
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [visibleBalances, setVisibleBalances] = useState({})

    useEffect(() => {
        getDashboard()
            .then(({ data }) => setData(data))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    const toggleBalance = (id) =>
        setVisibleBalances((v) => ({ ...v, [id]: !v[id] }))

    if (loading) return <><Navbar /><div className="page-loading"><span className="spinner" /></div></>

    const accounts = data?.accounts ?? []
    const totalBalance = accounts.reduce((s, a) => s + parseFloat(a.balance), 0)

    return (
        <>
            <Navbar />
            <div className="page">
                {/* Welcome banner */}
                <div className="db-welcome card">
                    <div>
                        <p className="db-greeting">Welcome back,</p>
                        <h1 className="db-name">{data?.user_name}</h1>
                        {data?.last_login && (
                            <p className="db-last-login">Last login: {data.last_login}</p>
                        )}
                    </div>
                    <div className="db-badges">
                        <span className="badge badge-primary">🏦 Banking-grade security</span>
                        <span className="badge badge-success">✔ Verified Account</span>
                    </div>
                </div>

                {/* Total balance */}
                <div className="db-total-row">
                    <div className="db-total card">
                        <p className="db-total-label">Total Portfolio Value</p>
                        <p className="db-total-amount">{fmtCurrency(totalBalance)}</p>
                    </div>
                    <div className="db-quicklinks card">
                        <p className="db-ql-title">Quick Links</p>
                        <div className="db-ql-grid">
                            <Link to="/transfer" className="ql-item">
                                <span className="ql-icon">💸</span>
                                <span>Send Money</span>
                            </Link>
                            <Link to="/profile" className="ql-item">
                                <span className="ql-icon">👤</span>
                                <span>My Profile</span>
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Account cards */}
                <h2 className="section-title" style={{ marginTop: 28 }}>Account Overview</h2>
                <p className="section-sub">Your primary savings & current accounts</p>

                <div className="accounts-grid">
                    {accounts.map((acc) => (
                        <div key={acc.account_id} className="account-card card">
                            <div className="acc-card-top">
                                <span className="badge badge-primary">{acc.account_type}</span>
                                <Link to={`/history/${acc.account_id}`} className="btn btn-secondary" style={{ fontSize: 12, padding: '5px 12px' }}>
                                    View History
                                </Link>
                            </div>
                            <div className="acc-number-row">
                                <span className="acc-number-label">A/C</span>
                                <span className="acc-number">
                                    {visibleBalances[acc.account_id]
                                        ? acc.account_number
                                        : `•••• •••• ${acc.account_number.slice(-4)}`}
                                    <button className="vis-toggle" onClick={() => toggleBalance(acc.account_id)}>
                                        {visibleBalances[acc.account_id] ? '🙈' : '👁'}
                                    </button>
                                </span>
                            </div>
                            <div className="acc-branch">{acc.branch_name} · {acc.ifsc_code}</div>

                            <div className="acc-balance-block">
                                <p className="acc-balance-label">Available Balance</p>
                                <p className="acc-balance">{fmtCurrency(acc.balance)}</p>
                            </div>

                            <BalanceForecast accountId={acc.account_id} />

                            <Link to="/transfer" className="btn btn-primary btn-full" style={{ marginTop: 16 }}>
                                Transfer Funds
                            </Link>
                        </div>
                    ))}
                </div>
            </div>
        </>
    )
}

function BalanceForecast({ accountId }) {
    const [forecast, setForecast] = useState(null)
    const [loading, setLoading] = useState(false)

    const fetchForecast = () => {
        setLoading(true)
        fetch(`/api/forecast/${accountId}`)
            .then(res => res.json())
            .then(data => {
                if (data.ok) setForecast(data.predictions)
            })
            .catch(console.error)
            .finally(() => setLoading(false))
    }

    if (!forecast) {
        return (
            <button className="btn-forecast-load" onClick={fetchForecast} disabled={loading}>
                {loading ? 'Analyzing...' : '📈 Predict 7-Day Trend'}
            </button>
        )
    }

    return (
        <div className="ai-forecast-box">
            <p className="ai-title">AI Balance Projection</p>
            <div className="forecast-items">
                {forecast.map((f, i) => (
                    <div key={i} className="forecast-point">
                        <span className="forecast-date">{f.date.slice(5)}</span>
                        <span className="forecast-val">{fmtCurrency(f.predicted_balance)}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}
