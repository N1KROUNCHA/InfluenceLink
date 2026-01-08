import { useQuery } from '@tanstack/react-query'
import { authAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'

export default function BrandProfile() {
    const navigate = useNavigate()

    const { data: profile, isLoading } = useQuery({
        queryKey: ['brand-profile'],
        queryFn: () => authAPI.profile().then(res => res.data)
    })

    const handleLogout = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        navigate('/login')
    }

    if (isLoading) {
        return <div className="flex justify-center py-20 animate-pulse text-primary-600 font-bold">Loading Brand Identity...</div>
    }

    const details = profile?.domain_details || {}
    const user = profile?.user || {}

    return (
        <div className="max-w-4xl mx-auto py-12 px-4">
            <div className="card bg-white shadow-2xl border-none overflow-hidden rounded-3xl">
                {/* Header Section */}
                <div className="h-32 bg-gradient-to-r from-primary-600 to-violet-700 p-8 flex justify-between items-center text-white">
                    <div>
                        <h1 className="text-3xl font-black tracking-tight">{details.brand_name || user.name}</h1>
                        <p className="text-sm font-medium text-white/70 uppercase tracking-widest">{details.industry} Domain</p>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="px-6 py-2 bg-white/10 hover:bg-red-500/80 text-white rounded-xl font-black text-sm transition-all border border-white/20 backdrop-blur-md"
                    >
                        Logout Securely
                    </button>
                </div>

                <div className="p-10">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                        {/* Left Column: Details */}
                        <div className="space-y-8">
                            <div>
                                <h2 className="text-xs font-black text-gray-400 uppercase tracking-[0.2em] mb-4">Registration Integrity</h2>
                                <div className="space-y-5">
                                    <div className="flex justify-between border-b border-gray-50 pb-3">
                                        <span className="text-sm font-bold text-gray-500">Official Brand Name</span>
                                        <span className="text-sm font-black text-gray-900">{details.brand_name}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-50 pb-3">
                                        <span className="text-sm font-bold text-gray-500">Contact Email</span>
                                        <span className="text-sm font-black text-gray-900">{user.email}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-50 pb-3">
                                        <span className="text-sm font-bold text-gray-500">Industry Segment</span>
                                        <span className="text-sm font-black text-primary-600">{details.industry}</span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-50 pb-3">
                                        <span className="text-sm font-bold text-gray-500">Brand Website</span>
                                        <span className="text-sm font-black text-blue-600 underline">
                                            {details.website ? <a href={details.website} target="_blank" rel="noreferrer">{details.website}</a> : 'Not Linked'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between border-b border-gray-50 pb-3">
                                        <span className="text-sm font-bold text-gray-500">Member Since</span>
                                        <span className="text-sm font-black text-gray-900">{new Date(details.joined).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Right Column: Security/Status */}
                        <div className="bg-gray-50/50 p-8 rounded-2xl border border-gray-100 flex flex-col justify-between">
                            <div>
                                <h3 className="text-sm font-black text-gray-900 mb-4 tracking-tight flex items-center gap-2">
                                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                                    Account Verification
                                </h3>
                                <p className="text-xs text-gray-600 leading-relaxed font-medium">
                                    Your brand entity is currently verified and in good standing. You have full access to campaign rankings and real-time ROI predictions.
                                </p>
                            </div>

                            <div className="mt-8 pt-6 border-t border-gray-200">
                                <div className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1">Security Token Status</div>
                                <div className="text-xs font-black text-primary-600 font-mono">ENCRYPTED_JWT_ACTIVE</div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-12 bg-primary-50 p-6 rounded-2xl border border-primary-100 text-center">
                        <p className="text-xs text-primary-700 font-bold tracking-tight">
                            Need to change your brand details? Contact InfluenceLink institutional support.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
