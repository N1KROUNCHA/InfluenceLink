import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { workflowAPI, influencersAPI } from '../services/api'

export default function InfluencerDashboard() {
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    const { data: collaborations, isLoading: collabLoading } = useQuery({
        queryKey: ['influencer-collaborations'],
        queryFn: () => workflowAPI.getInfluencerWorkflow(user.id).then(res => res.data),
        enabled: !!user.id
    })

    const { data: influencerProfile } = useQuery({
        queryKey: ['my-profile', user.id],
        queryFn: () => influencersAPI.get(user.id).then(res => res.data),
        enabled: !!user.id
    })

    // Filter collaborations for stats
    const activeCollabs = collaborations?.filter(c => c.status !== 'completed' && c.status !== 'rejected') || []
    const completedCollabs = collaborations?.filter(c => c.status.toLowerCase() === 'completed') || []

    const stats = [
        { label: 'Active Collaborations', value: collabLoading ? '...' : activeCollabs.length, color: 'text-violet-600', bg: 'bg-violet-50' },
        { label: 'Completed', value: collabLoading ? '...' : completedCollabs.length, color: 'text-emerald-600', bg: 'bg-emerald-50' },
        { label: 'Marketplace Score', value: influencerProfile ? (influencerProfile.engagement_score * 10).toFixed(1) : '...', color: 'text-amber-600', bg: 'bg-amber-50' },
        { label: 'Est. Reach', value: influencerProfile ? (influencerProfile.subscriber_count / 10).toLocaleString() : '...', color: 'text-primary-600', bg: 'bg-primary-50' },
    ]

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-black text-gray-900 tracking-tight">Welcome back, {user.name}</h1>
                    <p className="mt-2 text-gray-500 font-medium tracking-wide">Here's what's happening with your brand partnerships today.</p>
                </div>
                <div className="flex gap-3">
                    <Link to="/studio" className="btn bg-violet-600 hover:bg-violet-700 text-white shadow-xl shadow-violet-200 border-none px-6 py-3 font-black tracking-tight">
                        Open AI Content Studio
                    </Link>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {stats.map((stat, i) => (
                    <div key={i} className={`card ${stat.bg} border-none group hover:scale-[1.02] transition-all duration-300`}>
                        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-1">{stat.label}</div>
                        <div className={`text-4xl font-black ${stat.color} tracking-tighter`}>{stat.value}</div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Collaboration Feed */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-black text-gray-900 border-l-4 border-violet-500 pl-4 tracking-tight">Active Partnerships</h2>
                        <Link to="/collaborations" className="text-sm font-bold text-violet-600 hover:text-violet-800">View All →</Link>
                    </div>

                    {collabLoading ? (
                        <div className="space-y-4">
                            {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-100 rounded-2xl animate-pulse"></div>)}
                        </div>
                    ) : activeCollabs.length > 0 ? (
                        <div className="space-y-4">
                            {activeCollabs.slice(0, 5).map((collab, idx) => (
                                <div key={idx} className="card bg-white border-gray-100 hover:shadow-xl transition-all duration-500 group">
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <div className="text-[10px] font-black text-violet-500 uppercase tracking-widest mb-1">{collab.campaign_title}</div>
                                            <h3 className="text-lg font-black text-gray-900 group-hover:text-violet-600 transition-colors">{collab.brand_name || 'Brand Partner'}</h3>
                                        </div>
                                        <div className="text-right">
                                            <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${collab.status === 'negotiation' ? 'bg-amber-100 text-amber-700' :
                                                collab.status === 'content_creation' ? 'bg-blue-100 text-blue-700' :
                                                    'bg-violet-100 text-violet-700'
                                                }`}>
                                                {collab.status.replace('_', ' ')}
                                            </span>
                                            <div className="text-[9px] text-gray-400 mt-2 font-bold uppercase tracking-tighter">Updated: {new Date(collab.updated_at).toLocaleDateString()}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="card border-2 border-dashed border-gray-200 bg-gray-50/50 py-12 text-center">
                            <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center text-3xl mx-auto mb-4">🤝</div>
                            <p className="text-gray-500 font-bold">No active partnerships yet.</p>
                            <p className="text-xs text-gray-400 mt-1">Make sure your profile is optimized to attract more brands!</p>
                        </div>
                    )}
                </div>

                {/* Sidebar: AI Tips & Profile Snapshot */}
                <div className="space-y-6">
                    <div className="card bg-gray-900 text-white border-none shadow-2xl overflow-hidden relative">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-violet-600/20 rounded-full -mr-16 -mt-16 blur-3xl"></div>
                        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-violet-400 mb-4">AI Profile Tip</h3>
                        <p className="text-sm font-medium leading-relaxed text-gray-300">
                            "Creators in the <b>{influencerProfile?.category || 'Lifestyle'}</b> space are seeing a 15% increase in brand interest by adding <b>Instagram</b> handles to their bios."
                        </p>
                        <Link to="/profile" className="mt-6 inline-flex items-center gap-2 text-xs font-black text-white hover:text-violet-400 transition-colors uppercase tracking-widest">
                            Optimize Profile →
                        </Link>
                    </div>

                    <div className="card border-gray-200 shadow-sm">
                        <h3 className="text-xs font-black uppercase tracking-widest text-gray-400 mb-4">Channel DNA Preview</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center py-2 border-b border-gray-50">
                                <span className="text-xs font-bold text-gray-600">Category</span>
                                <span className="text-xs font-black text-gray-900 italic">{influencerProfile?.category}</span>
                            </div>
                            <div className="flex justify-between items-center py-2 border-b border-gray-50">
                                <span className="text-xs font-bold text-gray-600">Engagement</span>
                                <span className="text-xs font-black text-emerald-600">{(influencerProfile?.engagement_score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="flex justify-between items-center py-2">
                                <span className="text-xs font-bold text-gray-600">Authenticity</span>
                                <span className="text-xs font-black text-violet-600">{(influencerProfile?.authenticity_score * 100).toFixed(0)}/100</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
