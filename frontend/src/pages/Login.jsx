import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'

export default function Login() {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        type: 'brand' // default
    })
    const [error, setError] = useState('')

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        try {
            const res = await authAPI.login(formData)
            const { access_token, user } = res.data

            // Store token
            localStorage.setItem('token', access_token)
            localStorage.setItem('user', JSON.stringify(user))

            // Redirect based on type
            if (user.type === 'influencer') {
                // Check if onboarded (this logic requires backend to return onboarding status, 
                // or we simply redirect to dashboard and let them navigate)
                // For now, redirect to Onboarding if they want to update channel, or Dashboard.
                navigate('/onboard')
            } else {
                navigate('/')
            }

        } catch (err) {
            console.error(err)
            const msg = err.response?.data?.detail || 'Login failed'
            alert('Login Error: ' + msg) // Debug alert
            setError(msg)
        }
    }

    // Wrap handleSubmit to ensure debugging
    const onSubmit = async (e) => {
        e.preventDefault()
        console.log("Submitting login...")
        try {
            const res = await authAPI.login(formData)
            console.log("Login res:", res.data)

            const { access_token, user } = res.data

            if (!access_token) {
                alert("No access token received!")
                return
            }

            // Store token
            localStorage.setItem('token', access_token)
            localStorage.setItem('user', JSON.stringify(user))

            // Debug alert
            // alert(`Login Success! Token: ${access_token.substring(0, 10)}... Navigating...`)

            // Force navigation
            if (user.type === 'influencer') {
                window.location.href = '/onboard'
            } else {
                window.location.href = '/'
            }

        } catch (err) {
            console.error(err)
            const msg = err.response?.data?.detail || 'Login failed'
            alert('Login Error: ' + msg)
            setError(msg)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="card max-w-md w-full p-8 bg-white shadow-xl">
                <h2 className="text-3xl font-bold text-center mb-8 bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-fuchsia-600">
                    Welcome Back
                </h2>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={onSubmit} className="space-y-4">
                    <div>
                        <label className="label">I am a...</label>
                        <div className="flex gap-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="type"
                                    value="brand"
                                    checked={formData.type === 'brand'}
                                    onChange={handleChange}
                                    className="radio radio-primary"
                                />
                                <span className="font-medium">Brand</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    name="type"
                                    value="influencer"
                                    checked={formData.type === 'influencer'}
                                    onChange={handleChange}
                                    className="radio radio-secondary"
                                />
                                <span className="font-medium">Influencer</span>
                            </label>
                        </div>
                    </div>

                    <div>
                        <label className="label">Email</label>
                        <input
                            type="email"
                            name="email"
                            className="input w-full"
                            required
                            value={formData.email}
                            onChange={handleChange}
                        />
                    </div>

                    <div>
                        <label className="label">Password</label>
                        <input
                            type="password"
                            name="password"
                            className="input w-full"
                            required
                            value={formData.password}
                            onChange={handleChange}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary w-full mt-6">
                        Log In
                    </button>
                </form>

                <div className="mt-6 text-center text-sm text-gray-500">
                    Don't have an account? <Link to="/register" className="text-violet-600 font-semibold hover:underline">Sign up</Link>
                </div>
            </div>
        </div>
    )
}
