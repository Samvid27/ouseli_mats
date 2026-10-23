import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Login.css'

export default function Login() {
    const { login } = useAuth()
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)
        try {
            const data = await login(email, password)
            if (data.ok) {
                navigate('/dashboard')
            } else {
                const messages = {
                    INVALID_CREDENTIALS: 'Invalid email or password.',
                    MISSING_FIELDS: 'Please fill in all fields.',
                    DB_CONNECTION: 'Database connection error. Try again.',
                }
                setError(messages[data.error] || 'Login failed. Please try again.')
            }
        } catch {
            setError('Login failed. Check your connection.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-page">
            <div className="login-glow" />

            <div className="login-wrapper">
                {/* Left panel */}
                <div className="login-card">
                    <div className="login-header">
                        <div className="login-logo">
                            <span className="logo-icon-lg">SB</span>
                            <div>
                                <h1 className="login-brand">SecureBank</h1>
                                <p className="login-brand-sub">Digital Banking Platform</p>
                            </div>
                        </div>
                        <span className="secure-pill">🔒 Secure Login</span>
                    </div>

                    <form className="login-form" onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label className="form-label">Email Address</label>
                            <input
                                className="form-input"
                                type="email"
                                placeholder="you@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                autoFocus
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <input
                                className="form-input"
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        {error && <div className="login-error">{error}</div>}

                        <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
                            {loading ? <span className="spinner-sm" /> : null}
                            {loading ? 'Signing in…' : 'Sign in securely'}
                        </button>
                    </form>

                    <div className="login-demo">
                        <p className="demo-title">Demo Credentials</p>
                        <div className="demo-rows">
                            <span>john.doe@email.com</span><span>password123</span>
                        </div>
                        <div className="demo-rows">
                            <span>jane.smith@email.com</span><span>password456</span>
                        </div>
                    </div>
                </div>

                {/* Right panel */}
                <div className="login-info">
                    <h2>Banking with confidence</h2>
                    <ul className="info-list">
                        <li><span className="info-dot" />ACID-compliant fund transfers</li>
                        <li><span className="info-dot" />Row-level concurrency control</li>
                        <li><span className="info-dot" />Automatic audit logging via triggers</li>
                        <li><span className="info-dot" />B+ Tree indexed transaction history</li>
                        <li><span className="info-dot" />BCNF normalized schema</li>
                    </ul>
                    <div className="info-footer">BCSE302L DBMS Project</div>
                </div>
            </div>
        </div>
    )
}
