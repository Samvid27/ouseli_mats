import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import { getProfile } from '../api'
import './Profile.css'

function fmtDate(ts) {
    if (!ts) return '—'
    return new Date(ts).toLocaleDateString('en-IN', { dateStyle: 'long' })
}

function fmtCurrency(n) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(n)
}

export default function Profile() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        getProfile()
            .then(({ data }) => setData(data))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [])

    if (loading) return <><Navbar /><div className="page-loading"><span className="spinner" /></div></>

    const c = data?.customer
    const accounts = data?.accounts ?? []

    return (
        <>
            <Navbar />
            <div className="page">
                <div className="prof-header">
                    <div className="prof-avatar-wrap">
                        <div className="prof-avatar">{c?.full_name?.[0]}</div>
                    </div>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <h1 className="section-title">{c?.full_name}</h1>
                            <span className="badge badge-success">✔ Verified</span>
                        </div>
                        <p className="section-sub" style={{ marginBottom: 0 }}>Member since {fmtDate(c?.created_at)}</p>
                    </div>
                </div>

                <div className="prof-grid">
                    {/* Personal info card */}
                    <div className="card">
                        <h2 className="prof-card-title">Personal Information</h2>
                        <div className="prof-rows">
                            <div className="prof-row">
                                <span className="prof-key">Full Name</span>
                                <span className="prof-val">{c?.full_name}</span>
                            </div>
                            <div className="prof-row">
                                <span className="prof-key">Email</span>
                                <span className="prof-val">{c?.email}</span>
                            </div>
                            <div className="prof-row">
                                <span className="prof-key">Phone</span>
                                <span className="prof-val">{c?.phone ?? '—'}</span>
                            </div>
                            <div className="prof-row">
                                <span className="prof-key">Customer ID</span>
                                <span className="prof-val">#{c?.customer_id}</span>
                            </div>
                            <div className="prof-row">
                                <span className="prof-key">Member Since</span>
                                <span className="prof-val">{fmtDate(c?.created_at)}</span>
                            </div>
                        </div>
                    </div>

                    {/* Linked accounts */}
                    <div className="card">
                        <h2 className="prof-card-title">Linked Accounts</h2>
                        <div className="prof-accounts">
                            {accounts.map((a) => (
                                <div key={a.account_id} className="prof-account">
                                    <div className="prof-acc-top">
                                        <span className="badge badge-primary">{a.account_type}</span>
                                        <span className="prof-acc-balance">{fmtCurrency(a.balance)}</span>
                                    </div>
                                    <p className="prof-acc-number">{a.account_number}</p>
                                    <p className="prof-acc-branch">{a.branch_name}</p>
                                    <div className="prof-acc-meta">
                                        <span>IFSC: {a.ifsc_code}</span>
                                        <span>Since {fmtDate(a.created_at)}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* DB concepts note */}
                <div className="card prof-note">
                    <h3 className="prof-note-title">Database Concepts</h3>
                    <div className="prof-note-grid">
                        <div className="prof-note-item">
                            <p className="conf-item-label">Normalization</p>
                            <p className="prof-note-desc">Schema in BCNF — no redundancy across tables.</p>
                        </div>
                        <div className="prof-note-item">
                            <p className="conf-item-label">Indexing</p>
                            <p className="prof-note-desc">B+ Tree index on email for O(log n) lookup.</p>
                        </div>
                        <div className="prof-note-item">
                            <p className="conf-item-label">FK Constraints</p>
                            <p className="prof-note-desc">Accounts cascade-delete when customer is removed.</p>
                        </div>
                        <div className="prof-note-item">
                            <p className="conf-item-label">JOIN</p>
                            <p className="prof-note-desc">INNER JOIN between Customers ↔ Accounts.</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}
