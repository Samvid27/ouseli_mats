import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Navbar.css'

export default function Navbar() {
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = async () => {
        await logout()
        navigate('/login')
    }

    return (
        <nav className="navbar">
            <div className="navbar-left">
                <Link to="/dashboard" className="navbar-logo">
                    <span className="logo-icon">SB</span>
                    <span className="logo-text">SecureBank</span>
                    <span className="logo-sub">Digital Banking</span>
                </Link>
            </div>
            <div className="navbar-center">
                <Link to="/dashboard" className="nav-link">Home</Link>
                <Link to="/transfer" className="nav-link">Send Money</Link>
                <Link to="/profile" className="nav-link">Profile</Link>
            </div>
            <div className="navbar-right">
                {user && (
                    <>
                        <div className="nav-avatar">{user.name?.[0] ?? 'U'}</div>
                        <span className="nav-username">{user.name?.split(' ')[0]}</span>
                    </>
                )}
                <button className="btn-logout" onClick={handleLogout}>Logout</button>
            </div>
        </nav>
    )
}
