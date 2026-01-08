import React, { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { authAPI } from '../services/api'

export default function InfluencerProfileEdit() {
    const [formData, setFormData] = useState({
        channel_name: '',
        category: '',
        description: ''
    })
    const [message, setMessage] = useState('')

    const { data: profileData, isLoading } = useQuery({
        queryKey: ['profile'],
        queryFn: () => authAPI.profile().then(res => res.data)
    })

    useEffect(() => {
        if (profileData?.domain_details) {
            setFormData({
                channel_name: profileData.domain_details.channel_name || '',
                category: profileData.domain_details.category || '',
                description: profileData.domain_details.description || ''
            })
        }
    }, [profileData])

    const updateMutation = useMutation({
        mutationFn: (data) => authAPI.updateInfluencerProfile(data),
        onSuccess: () => {
            setMessage('Profile updated successfully! ✨')
            setTimeout(() => setMessage(''), 3000)
        },
        onError: (err) => setMessage('Error: ' + err.message)
    })

    const handleSubmit = (e) => {
        e.preventDefault()
        updateMutation.mutate(formData)
    }

    if (isLoading) return <div className="p-8 text-center animate-pulse">Loading Identity Matrix...</div>

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-700">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-black text-gray-900 tracking-tight">Marketplace Identity</h1>
                    <p className="mt-2 text-gray-500 font-medium tracking-wide">Manage how your channel appears to potential brand partners.</p>
                </div>
                <div className="text-right">
                    <div className="text-[10px] font-black uppercase tracking-widest text-gray-400">Registry Status</div>
                    <div className="text-emerald-600 font-black text-xs uppercase tracking-widest mt-1">Verified Creator</div>
                </div>
            </div>

            {message && (
                <div className={`p-4 rounded-2xl font-bold text-center animate-in slide-in-from-top-2 ${message.includes('Error') ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100 shadow-sm'}`}>
                    {message}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                    <form onSubmit={handleSubmit} className="card bg-white shadow-xl shadow-gray-200/50 border-gray-100 p-8 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 ml-1">Channel Display Name</label>
                                <input
                                    type="text"
                                    className="w-full bg-gray-50 border-none rounded-2xl p-4 text-sm font-bold text-gray-900 focus:ring-2 focus:ring-primary-500 transition-all"
                                    value={formData.channel_name}
                                    onChange={(e) => setFormData({ ...formData, channel_name: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 ml-1">Marketplace Category</label>
                                <select
                                    className="w-full bg-gray-50 border-none rounded-2xl p-4 text-sm font-bold text-gray-900 focus:ring-2 focus:ring-primary-500 transition-all appearance-none"
                                    value={formData.category}
                                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                >
                                    <option value="Gaming">Gaming</option>
                                    <option value="Beauty">Beauty</option>
                                    <option value="Finance">Finance</option>
                                    <option value="Tech">Tech</option>
                                    <option value="Lifestyle">Lifestyle</option>
                                    <option value="Fashion">Fashion</option>
                                    <option value="Business">Business</option>
                                </select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-widest text-gray-400 ml-1">Channel Description (Visible to Brands)</label>
                            <textarea
                                rows="6"
                                className="w-full bg-gray-50 border-none rounded-2xl p-4 text-sm font-medium text-gray-700 focus:ring-2 focus:ring-primary-500 transition-all leading-relaxed"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                        </div>

                        <div className="pt-4">
                            <button
                                type="submit"
                                disabled={updateMutation.isLoading}
                                className="w-full bg-gray-900 hover:bg-black text-white font-black py-4 rounded-2xl shadow-xl shadow-gray-200 border-none transition-all flex items-center justify-center gap-2 group"
                            >
                                {updateMutation.isLoading ? 'Processing...' : 'Save Registry Changes'}
                                <span className="group-hover:translate-x-1 transition-transform">→</span>
                            </button>
                        </div>
                    </form>
                </div>

                <div className="space-y-6">
                    <div className="card bg-violet-600 text-white border-none shadow-xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
                        <h3 className="text-[10px] font-black uppercase tracking-widest text-violet-200 mb-4">DNA Snapshot</h3>
                        <div className="space-y-4">
                            <div>
                                <div className="text-[9px] font-black uppercase text-violet-300 opacity-60">Transparency Score</div>
                                <div className="text-2xl font-black">94.2%</div>
                            </div>
                            <div>
                                <div className="text-[9px] font-black uppercase text-violet-300 opacity-60">Brand Safety</div>
                                <div className="text-2xl font-black text-emerald-300">Certified</div>
                            </div>
                        </div>
                    </div>

                    <div className="card bg-gray-50 border-gray-100 border-2 border-dashed">
                        <h3 className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4 text-center">Audit Insight</h3>
                        <p className="text-xs text-gray-500 text-center font-medium italic">
                            "Updating your description to mention specific niches like <b>Web3</b> or <b>ESG</b> can improve AI discovery by up to 22%."
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
