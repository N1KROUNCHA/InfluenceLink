import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'

export default function InfluencerOnboarding() {
    const navigate = useNavigate()
    const [handle, setHandle] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const user = JSON.parse(localStorage.getItem('user') || '{}')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            await authAPI.onboard({
                user_id: user.id,
                youtube_handle: handle
            })
            alert('Channel connected successully! DNA Generated.')
            navigate('/dashboard') // Or influencer specific dashboard
        } catch (err) {
            setError(err.response?.data?.detail || 'Onboarding failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="card max-w-lg w-full p-8 bg-white shadow-xl text-center">
                <div className="text-6xl mb-6">🎥</div>
                <h2 className="text-3xl font-bold mb-2">Connect Your Channel</h2>
                <p className="text-gray-500 mb-8">
                    Paste your YouTube handle (e.g. @MKBHD) to automatically import your stats and generate your AI Influence DNA.
                </p>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm text-left">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="text-left">
                        <label className="label">YouTube Handle / URL</label>
                        <input
                            type="text"
                            className="input w-full text-lg"
                            placeholder="@YourChannel"
                            required
                            value={handle}
                            onChange={(e) => setHandle(e.target.value)}
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary w-full text-lg py-3"
                        disabled={loading}
                    >
                        {loading ? 'Analyzing Channel...' : 'Connect & Generate DNA'}
                    </button>
                </form>
            </div>
        </div>
    )
}
