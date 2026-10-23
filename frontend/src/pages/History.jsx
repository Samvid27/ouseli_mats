import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getHistory, getDashboard } from '../api'
import './History.css'

function fmtDate(ts) {
    if (!ts) return '—'
    return new Date(ts).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

function fmtCurrency(n) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(n)
}

export default function History() {
    const { accountId } = useParams()
    const [data, setData] = useState(null)
    const [accounts, setAccounts] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedId, setSelectedId] = useState(accountId)

    useEffect(() => {
        getDashboard().then(({ data }) => setAccounts(data.accounts ?? []))
    }, [])

    useEffect(() => {
        if (!selectedId) return
        setLoading(true)
        getHistory(selectedId)
            .then(({ data }) => setData(data))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [selectedId])

    const acc = data?.account
    const txns = data?.transactions ?? []
    const numId = parseInt(selectedId)

    return (
        <>
            <Navbar />
            <div className="page">
                <div className="hist-header">
                    <div>
                        <h1 className="section-title">Transaction History</h1>
                        <p className="section-sub">Indexed by B+ Tree on <code>transaction_timestamp</code> for fast retrieval</p>
                    </div>
                    {accounts.length > 1 && (
                        <select
                            className="form-select"
                            style={{ width: 240 }}
                            value={selectedId}
                            onChange={(e) => setSelectedId(e.target.value)}
                        >
                            {accounts.map((a) => (
                                <option key={a.account_id} value={a.account_id}>
                                    {a.account_type} ···{a.account_number.slice(-4)}
                                </option>
                            ))}
                        </select>
                    )}
                </div>

                {acc && (
                    <div className="hist-acc-card card">
                        <div className="hist-acc-info">
                            <span className="badge badge-primary">{acc.account_type}</span>
                            <span className="hist-acc-num">A/C {acc.account_number}</span>
                            <span className="hist-acc-branch">{acc.branch_name} · {acc.ifsc_code}</span>
                        </div>
                        <div className="hist-acc-balance">
                            <p className="hist-bal-label">Current Balance</p>
                            <p className="hist-bal">{fmtCurrency(acc.balance)}</p>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="page-loading"><span className="spinner" /></div>
                ) : txns.length === 0 ? (
                    <div className="card hist-empty">No transactions found for this account.</div>
                ) : (
                    <div className="table-wrap" style={{ marginTop: 20 }}>
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Type</th>
                                    <th>From</th>
                                    <th>To</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>
                            <tbody>
                                {txns.map((t) => {
                                    const isSend = t.from_account_id === numId
                                    return (
                                        <tr key={t.transaction_id}>
                                            <td>#{t.transaction_id}</td>
                                            <td>{t.transaction_type}</td>
                                            <td>#{t.from_account_id ?? '—'}</td>
                                            <td>#{t.to_account_id}</td>
                                            <td>
                                                <span className={isSend ? 'amount-negative' : 'amount-positive'}>
                                                    {isSend ? '−' : '+'}{fmtCurrency(t.amount)}
                                                </span>
                                            </td>
                                            <td>
                                                <span className={`badge ${t.status === 'Success' ? 'badge-success' : 'badge-error'}`}>
                                                    {t.status}
                                                </span>
                                            </td>
                                            <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{fmtDate(t.transaction_timestamp)}</td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </>
    )
}
