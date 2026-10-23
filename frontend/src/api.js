import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    withCredentials: true,
})

export const login = (email, password) =>
    api.post('/login', { email, password })

export const logout = () => api.post('/logout')

export const getMe = () => api.get('/me')

export const getDashboard = () => api.get('/dashboard')

export const getProfile = () => api.get('/profile')

export const getHistory = (accountId) => api.get(`/history/${accountId}`)

export const doTransfer = (data) => api.post('/transfer', data)

export default api
