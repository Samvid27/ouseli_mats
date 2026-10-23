import { createContext, useContext, useState, useEffect } from 'react'
import { getMe, login as apiLogin, logout as apiLogout } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        getMe()
            .then(({ data }) => {
                if (data.authenticated) setUser(data.user)
            })
            .catch(() => { })
            .finally(() => setLoading(false))
    }, [])

    const login = async (email, password) => {
        const { data } = await apiLogin(email, password)
        if (data.ok) setUser(data.user)
        return data
    }

    const logout = async () => {
        await apiLogout()
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    return useContext(AuthContext)
}
