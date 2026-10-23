import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getDashboard, doTransfer } from '../api'
import './Transfer.css'

export default function Transfer() {
    const navigate = useNavigate()
    const [accounts, setAccounts] = useState([])
    const [form, setForm] = useState({
        from_account_id: '',
        to_account_number: '',
        beneficiary_name: '',
        bank_name: '',
        ifsc: '',
        amount: '',
    })
    const [loading, setLoading] = useState(false)
    const [toast, setToast] = useState(null)

    useEffect(() => {
        getDashboard().then(({ data }) => {
            setAccounts(data.accounts ?? [])
            if (data.accounts?.length) {
                setForm((f) => ({ ...f, from_account_id: data.accounts[0].account_id }))
            }
        })
    }, [])

    const showToast = (msg, type = 'success') => {
        setToast({ msg, type })
        setTimeout(() => setToast(null), 4000)
    }

    const handleChange = (e) =>
        setForm((f) => ({ ...f, [e.target.name]: e.target.value }))

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const { data } = await doTransfer({
                ...form,
                from_account_id: parseInt(form.from_account_id),
                amount: parseFloat(form.amount),
            })
            if (data.ok) {
                if (data.ai_risk_warning) {
                    showToast('⚠️ Suspiciously high amount detected by AI. Logged for review.', 'warning')
                } else {
                    showToast(data.message || 'Transfer successful! 🎉', 'success')
                }
                setForm((f) => ({ ...f, to_account_number: '', beneficiary_name: '', bank_name: '', ifsc: '', amount: '' }))
                setTimeout(() => navigate('/dashboard'), 3000)
            } else {
                const messages = {
                    MISSING_FIELDS: 'Please fill all fields.',
                    INVALID_AMOUNT: 'Amount must be greater than zero.',
                    DEST_NOT_FOUND: 'Destination account not found.',
                    FORBIDDEN: 'Not authorised to use that source account.',
                }
                showToast(data.message || messages[data.error] || 'Transfer failed.', 'error')
            }
        } catch (err) {
            showToast('Transfer failed. Please try again.', 'error')
        } finally {
            setLoading(false)
        }
    }

    const selectedAcc = accounts.find((a) => a.account_id == form.from_account_id)

    return (
        <>
            <Navbar />
            {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}

            <div className="page transfer-page">
                <div className="tf-grid">
                    {/* Form */}
                    <div className="card">
                        <h1 className="section-title">Transfer Funds</h1>
                        <p className="section-sub">ACID-compliant transaction via stored procedure</p>

                        <form className="tf-form" onSubmit={handleSubmit}>
                            {/* From account */}
                            <div className="form-group">
                                <label className="form-label">From Account</label>
                                <select className="form-select" name="from_account_id" value={form.from_account_id} onChange={handleChange} required>
                                    {accounts.map((a) => (
                                        <option key={a.account_id} value={a.account_id}>
                                            {a.account_type} — ···{a.account_number.slice(-4)} (₹{parseFloat(a.balance).toFixed(2)})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="divider" />

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Beneficiary Name</label>
                                    <input className="form-input" name="beneficiary_name" value={form.beneficiary_name} onChange={handleChange} placeholder="John Smith" required />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Bank Name</label>
                                    <input className="form-input" name="bank_name" value={form.bank_name} onChange={handleChange} placeholder="HDFC Bank" required />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Account Number</label>
                                    <input className="form-input" name="to_account_number" value={form.to_account_number} onChange={handleChange} placeholder="12-digit number" maxLength={12} required />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">IFSC Code</label>
                                    <input className="form-input" name="ifsc" value={form.ifsc} onChange={handleChange} placeholder="HDFC0001001" required />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Amount (₹)</label>
                                <input className="form-input tf-amount-input" name="amount" type="number" min="1" step="0.01" value={form.amount} onChange={handleChange} placeholder="0.00" required />
                            </div>

                            <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
                                {loading ? <span className="spinner-sm" /> : '🔐'}
                                {loading ? 'Processing…' : 'Transfer Securely'}
                            </button>
                        </form>
                    </div>

                    {/* ACID info panel */}
                    <div className="tf-side">
                        <div className="card tf-acid">
                            <h3 className="tf-acid-title">⚡ ACID Transaction</h3>
                            <ul className="tf-acid-list">
                                <li><strong>Atomicity</strong> — All or nothing. Partial transfers never happen.</li>
                                <li><strong>Consistency</strong> — Balance validation before deduction.</li>
                                <li><strong>Isolation</strong> — Row-level locks (<code>SELECT FOR UPDATE</code>).</li>
                                <li><strong>Durability</strong> — Committed changes survive crashes.</li>
                            </ul>
                        </div>
                        {selectedAcc && (
                            <div className="card tf-balance">
                                <p className="tf-bal-label">Available Balance</p>
                                <p className="tf-bal-amount">₹{parseFloat(selectedAcc.balance).toFixed(2)}</p>
                                <p className="tf-bal-acc">{selectedAcc.account_type} · ···{selectedAcc.account_number.slice(-4)}</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    )
}
