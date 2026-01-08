import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../services/api'

export default function Register() {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        type: 'brand',
        website: '',
        industry: ''
    })
    const [error, setError] = useState('')

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        try {
            await authAPI.register(formData)
            alert('Registration successful! Please login.')
            navigate('/login')
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12">
            <div className="card max-w-md w-full p-8 bg-white shadow-xl">
                <h2 className="text-3xl font-bold text-center mb-8 bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-fuchsia-600">
                    Create Account
                </h2>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
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
                        <label className="label">{formData.type === 'brand' ? 'Brand Name' : 'Channel Name'}</label>
                        <input
                            type="text"
                            name="name"
                            className="input w-full"
                            required
                            value={formData.name}
                            onChange={handleChange}
                        />
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

                    {formData.type === 'brand' && (
                        <>
                            <div>
                                <label className="label">Website</label>
                                <input
                                    type="text"
                                    name="website"
                                    className="input w-full"
                                    value={formData.website}
                                    onChange={handleChange}
                                />
                            </div>
                            <div>
                                <label className="label">Industry</label>
                                <input
                                    type="text"
                                    name="industry"
                                    className="input w-full"
                                    value={formData.industry}
                                    onChange={handleChange}
                                />
                            </div>
                        </>
                    )}

                    <button type="submit" className="btn btn-primary w-full mt-6">
                        Register
                    </button>
                </form>

                <div className="mt-6 text-center text-sm text-gray-500">
                    Already have an account? <Link to="/login" className="text-violet-600 font-semibold hover:underline">Login</Link>
                </div>
            </div>
        </div>
    )
}
