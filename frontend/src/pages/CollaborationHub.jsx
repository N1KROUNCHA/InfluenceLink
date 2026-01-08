import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { workflowAPI } from '../services/api'

export default function CollaborationHub() {
    const navigate = useNavigate()
    const user = JSON.parse(localStorage.getItem('user') || '{}')

    const { data: collaborations, isLoading } = useQuery({
        queryKey: ['influencer-collaborations'],
        queryFn: () => workflowAPI.getInfluencerWorkflow(user.id).then(res => res.data),
        enabled: !!user.id
    })

    // Group by status for a more structured view
    const grouped = collaborations?.reduce((acc, curr) => {
        if (!acc[curr.status]) acc[curr.status] = []
        acc[curr.status].push(curr)
        return acc
    }, {}) || {}

    const statusLabels = {
        'shortlisted': 'Discovery / Interest',
        'outreached': 'Open Proposal',
        'negotiating': 'Terms & Contracts',
        'contracted': 'Content Creation',
        'post_live': 'Live & Monitoring',
        'completed': 'Finished',
        'rejected': 'Declined'
    }

    return (
        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-black text-gray-900 tracking-tight">Collaboration Hub</h1>
                    <p className="mt-2 text-gray-500 font-medium tracking-wide">Manage your active brand partnerships and track campaign progress.</p>
                </div>
            </div>

            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map(i => <div key={i} className="h-64 bg-gray-100 rounded-2xl animate-pulse"></div>)}
                </div>
            ) : collaborations?.length > 0 ? (
                <div className="space-y-12">
                    {Object.entries(statusLabels).map(([status, label]) => {
                        const items = grouped[status] || []
                        if (items.length === 0) return null

                        return (
                            <div key={status} className="space-y-6">
                                <div className="flex items-center gap-4">
                                    <h2 className="text-sm font-black uppercase tracking-widest text-gray-400">{label}</h2>
                                    <div className="flex-1 h-px bg-gray-100"></div>
                                    <span className="bg-gray-100 text-gray-500 text-[10px] font-black px-2 py-0.5 rounded-full">{items.length}</span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {items.map((collab, idx) => (
                                        <div key={idx} className="card bg-white border-gray-100 hover:shadow-2xl hover:-translate-y-1 transition-all duration-500 group flex flex-col justify-between">
                                            <div>
                                                <div className="flex justify-between items-start mb-4">
                                                    <div className="w-12 h-12 rounded-2xl bg-primary-50 flex items-center justify-center text-primary-600 font-black text-xl shadow-inner group-hover:bg-primary-600 group-hover:text-white transition-colors duration-300">
                                                        {collab.brand_name ? collab.brand_name[0] : 'B'}
                                                    </div>
                                                    <span className={`px-2 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter ${status === 'contracted' ? 'bg-emerald-100 text-emerald-700' :
                                                        status === 'negotiating' ? 'bg-amber-100 text-amber-700' :
                                                            'bg-violet-100 text-violet-700'
                                                        }`}>
                                                        {status.replace('_', ' ')}
                                                    </span>
                                                </div>
                                                <h3 className="text-xl font-black text-gray-900 mb-1 group-hover:text-primary-600 transition-colors uppercase tracking-tight">{collab.campaign_title}</h3>
                                                <p className="text-sm font-bold text-gray-500 mb-4">{collab.brand_name}</p>

                                                {collab.notes && (
                                                    <div className="bg-gray-50 p-4 rounded-xl border border-gray-100 mb-4">
                                                        <div className="text-[10px] font-black uppercase text-gray-400 mb-2">Brand Instructions:</div>
                                                        <p className="text-xs text-gray-600 italic leading-relaxed line-clamp-3">"{collab.notes}"</p>
                                                    </div>
                                                )}
                                            </div>

                                            <div className="pt-4 border-t border-gray-50 flex items-center justify-between">
                                                <div className="text-[9px] font-black text-gray-400 uppercase tracking-widest">
                                                    Joined: {new Date(collab.updated_at).toLocaleDateString()}
                                                </div>
                                                <button
                                                    onClick={() => navigate(`/campaigns/${collab.campaign_id}`)}
                                                    className="text-xs font-black text-primary-600 hover:text-primary-800 uppercase tracking-widest flex items-center gap-1"
                                                >
                                                    Details ↗
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    })}
                </div>
            ) : (
                <div className="card bg-white border-2 border-dashed border-gray-200 py-24 text-center">
                    <div className="text-6xl mb-6">🏜️</div>
                    <h2 className="text-2xl font-black text-gray-900 mb-2">The Hub is Empty</h2>
                    <p className="text-gray-500 max-w-md mx-auto font-medium">You haven't been added to any campaigns yet. Our AI is actively pitching your DNA to relevant brands!</p>
                    <div className="mt-8 flex justify-center gap-4">
                        <button className="btn bg-gray-900 text-white font-black px-8 py-3 rounded-2xl hover:bg-black transition-all">
                            Optimize DNA
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
