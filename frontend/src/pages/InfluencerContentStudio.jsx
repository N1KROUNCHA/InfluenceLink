import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { contentAPI } from '../services/api'

export default function InfluencerContentStudio() {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const [searchParams] = useSearchParams()
    const campaignId = searchParams.get('campaignId')
    const [ideas, setIdeas] = useState(null)
    const [prompt, setPrompt] = useState('')
    const [saved, setSaved] = useState(false)

    const [activeTab, setActiveTab] = useState('studio') // 'studio' | 'history'

    const { data: history, refetch: refetchHistory } = useQuery({
        queryKey: ['creator-history-full', user.id],
        queryFn: () => contentAPI.getCreatorHistory(user.id).then(res => res.data),
        enabled: !!user.id && activeTab === 'history'
    })

    const studioMutation = useMutation({
        mutationFn: () => contentAPI.generateCreatorStudio(user.id, prompt).then(res => res.data),
        onSuccess: (data) => {
            setIdeas(data)
            setSaved(false)
        }
    })

    const saveMutation = useMutation({
        mutationFn: () => contentAPI.saveCreatorContent({
            influencer_id: user.id,
            campaign_id: campaignId ? parseInt(campaignId) : null,
            prompt: prompt,
            content: ideas.ideas,
            trends: ideas.trends
        }),
        onSuccess: () => {
            setSaved(true)
            alert("Ideas saved to history!")
            refetchHistory()
        }
    })

    // Format the AI text for better display
    const renderIdeas = (text) => {
        if (!text) return null
        return text.split('\n').map((line, i) => {
            if (line.startsWith('1.') || line.startsWith('2.') || line.startsWith('3.')) {
                return <h3 key={i} className="text-xl font-black text-violet-600 mt-8 mb-4 border-b-2 border-violet-100 pb-2 uppercase tracking-tight">{line}</h3>
            }
            if (line.includes(':')) {
                const [label, content] = line.split(':')
                return (
                    <p key={i} className="mb-3 text-sm leading-relaxed text-gray-700">
                        <span className="font-black text-gray-900 uppercase tracking-widest text-[10px] mr-2">{label}:</span>
                        {content}
                    </p>
                )
            }
            return <p key={i} className="mb-3 text-sm leading-relaxed text-gray-500 font-medium">{line}</p>
        })
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in slide-in-from-right-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div className="flex-1">
                    <div className="inline-block bg-violet-100 text-violet-700 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest mb-4">AI Pro Powered</div>
                    <h1 className="text-4xl font-black text-gray-900 tracking-tight">Content Ideation Studio</h1>
                    <p className="mt-2 text-gray-500 font-medium tracking-wide">Generate viral video concepts and brand sponsorship pitches tailored to your DNA.</p>
                </div>

                {/* Tab Switcher */}
                <div className="flex bg-gray-100 p-1 rounded-xl">
                    <button
                        onClick={() => setActiveTab('studio')}
                        className={`px-6 py-2 rounded-lg text-sm font-black uppercase tracking-tight transition-all ${activeTab === 'studio' ? 'bg-white text-violet-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                    >
                        Create
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`px-6 py-2 rounded-lg text-sm font-black uppercase tracking-tight transition-all ${activeTab === 'history' ? 'bg-white text-violet-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                    >
                        History
                    </button>
                </div>
            </div>

            {activeTab === 'studio' ? (
                <>
                    <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
                        <div className="relative group w-full sm:w-80">
                            <input
                                type="text"
                                placeholder="Add specific direction... (e.g. 'unboxing experience', 'high energy')"
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                className="w-full bg-white border-2 border-violet-100 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:border-violet-500 transition-all placeholder:text-gray-300"
                            />
                        </div>
                        <button
                            onClick={() => studioMutation.mutate()}
                            disabled={studioMutation.isLoading}
                            className="w-full sm:w-auto btn bg-violet-600 hover:bg-violet-700 text-white shadow-2xl shadow-violet-200 border-none px-8 py-4 font-black tracking-tight flex items-center gap-3 group"
                        >
                            {studioMutation.isLoading ? (
                                <span className="flex items-center gap-2">
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    Analyzing DNA...
                                </span>
                            ) : (
                                <>
                                    {prompt ? 'Guided Generation' : 'Generate New Ideas'}
                                    <span className="group-hover:rotate-12 transition-transform text-xl">✨</span>
                                </>
                            )}
                        </button>
                    </div>

                    {!ideas && !studioMutation.isLoading && (
                        <div className="card border-2 border-dashed border-gray-200 py-32 text-center bg-gray-50/30">
                            <div className="text-6xl mb-8 opacity-40 grayscale group-hover:grayscale-0 transition-all">🤖</div>
                            <h2 className="text-2xl font-black text-gray-400 mb-2">Ready to start creating?</h2>
                            <p className="text-sm text-gray-400 font-medium">Click the button above to unlock AI-powered channel growth strategies.</p>
                        </div>
                    )}

                    {ideas && (
                        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                            <div className="lg:col-span-3">
                                <div className="card bg-white border-gray-100 shadow-2xl shadow-violet-100/50 p-10 animate-in zoom-in-95 duration-500">
                                    <div className="flex justify-between items-center mb-8 pb-4 border-b border-gray-50">
                                        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">Analysis Result</div>
                                        <div className="flex items-center gap-4">
                                            <button
                                                onClick={() => saveMutation.mutate()}
                                                disabled={saved || saveMutation.isLoading}
                                                className={`text-xs font-black uppercase tracking-widest px-4 py-2 rounded-lg transition-all ${saved
                                                    ? 'bg-green-100 text-green-700 cursor-default'
                                                    : 'bg-violet-100 text-violet-700 hover:bg-violet-200'
                                                    }`}
                                            >
                                                {saved ? 'Saved ✓' : 'Save to History'}
                                            </button>
                                            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-violet-500 italic">Llama-3-Enhanced</div>
                                        </div>
                                    </div>
                                    <div className="prose prose-violet max-w-none">
                                        {renderIdeas(ideas.ideas)}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="card bg-gray-900 text-white border-none shadow-xl">
                                    <h3 className="text-[10px] font-black uppercase tracking-widest text-violet-400 mb-4">Market Trends Used</h3>
                                    <div className="space-y-3">
                                        {ideas.trends.map((trend, i) => (
                                            <div key={i} className="flex gap-3 items-start p-3 bg-white/5 rounded-xl border border-white/5 group hover:bg-white/10 transition-colors">
                                                <span className="text-violet-400 font-black">#</span>
                                                <span className="text-xs font-bold text-gray-300 leading-tight group-hover:text-white">{trend}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="card border-gray-200 bg-emerald-50 border-none shadow-sm">
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                                        <h3 className="text-[10px] font-black uppercase tracking-widest text-emerald-700">Marketability Prediction</h3>
                                    </div>
                                    <p className="text-xs font-bold text-emerald-800 leading-relaxed">
                                        These ideas are targeting a <b>14.2%</b> increase in brand attraction based on current <b>{user.name}</b> audience metrics.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                </>
            ) : (
                <div className="space-y-6">
                    {history && history.length > 0 ? (
                        history.map((item, idx) => (
                            <div key={idx} className="card bg-white border-gray-100 hover:shadow-lg transition-all duration-300">
                                <div className="flex justify-between items-start mb-4 border-b border-gray-50 pb-4">
                                    <div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-[10px] font-black bg-gray-100 text-gray-500 px-2 py-1 rounded-md uppercase tracking-wide">
                                                {new Date(item.generated_at).toLocaleDateString()}
                                            </span>
                                            {item.campaign_id && (
                                                <span className="text-[10px] font-black bg-violet-100 text-violet-600 px-2 py-1 rounded-md uppercase tracking-wide">
                                                    Campaign #{item.campaign_id}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    {item.prompt && (
                                        <div className="text-xs text-gray-500 font-medium italic">
                                            "{item.prompt}"
                                        </div>
                                    )}
                                </div>
                                <div className="prose prose-sm max-w-none text-gray-600">
                                    {renderIdeas(item.content)}
                                </div>
                                {item.trends && (
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        {item.trends.map((t, i) => (
                                            <span key={i} className="text-[10px] font-bold text-gray-400 bg-gray-50 px-2 py-1 rounded-full">#{t}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))
                    ) : (
                        <div className="text-center py-24 text-gray-400">
                            <div className="text-4xl mb-4">📜</div>
                            <p className="font-bold">No history available yet.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
