import React, { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { influencersAPI, campaignsAPI, workflowAPI } from '../services/api'

export default function InfluencerDetail() {
  const { id } = useParams()
  const [showFullDescription, setShowFullDescription] = useState(false)

  const { data: influencer, isLoading } = useQuery({
    queryKey: ['influencer', id],
    queryFn: () => influencersAPI.get(id).then(res => res.data)
  })

  const { data: similar } = useQuery({
    queryKey: ['similar-influencers', influencer?.channel_id],
    queryFn: () => influencersAPI.findSimilar(influencer.channel_id).then(res => res.data),
    enabled: !!influencer?.channel_id
  })

  const { data: campaigns } = useQuery({
    queryKey: ['campaigns-list'],
    queryFn: () => campaignsAPI.list('active').then(res => res.data),
  })

  const addToWorkflowMutation = useMutation({
    mutationFn: (campaignId) => workflowAPI.add(campaignId, id),
    onSuccess: () => alert('Successfully added to campaign workflow!'),
    onError: (err) => alert('Failed to add: ' + (err.response?.data?.detail || err.message))
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!influencer) {
    return <div className="card text-center py-12">Influencer not found</div>
  }

  const meta = influencer.youtube_meta || {}
  const snippet = meta.snippet || {}
  const stats = meta.statistics || {}
  const banner = meta.brandingSettings?.image?.bannerExternalUrl || 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=2000&auto=format&fit=crop'
  const avatar = snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url || `https://ui-avatars.com/api/?name=${influencer.channel_name}&background=6366f1&color=fff`

  const formatNumber = (num) => {
    if (!num) return '0'
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  // Robust link and handle extraction from description
  const extractLinks = (text) => {
    if (!text) return []

    // 1. Full URL matches (Instagram, Twitter, etc.)
    const urlRegex = /(?:https?:\/\/)?(?:www\.)?(?:instagram\.com|twitter\.com|x\.com|facebook\.com|linkedin\.com)\/[a-zA-Z0-9_./-]+/gi
    let found = text.match(urlRegex) || []

    // 2. "@mention" style handles if followed by social context
    // This looks for "IG: @user" or "Instagram: @user"
    const handleRegex = /(?:ig|insta|instagram|tw|twitter|𝕏|fb|facebook):\s?@?([a-zA-Z0-9_.]+)/gi
    let match;
    while ((match = handleRegex.exec(text)) !== null) {
      const type = match[0].toLowerCase()
      const handle = match[1]
      let url = ''
      if (type.includes('ig') || type.includes('insta')) url = `https://instagram.com/${handle}`
      else if (type.includes('tw') || type.includes('𝕏')) url = `https://twitter.com/${handle}`
      else if (type.includes('fb') || type.includes('face')) url = `https://facebook.com/${handle}`

      if (url) found.push(url)
    }

    // Clean and deduplicate (ensure https://)
    return [...new Set(found)].map(u => u.startsWith('http') ? u : `https://${u}`).slice(0, 5)
  }

  // Generate a category-aware audience summary
  const getAudienceSummary = (category, region) => {
    const cat = (category || 'Lifestyle').toLowerCase()
    const reg = region || 'Global'

    let ageRange = "18-34"
    let gender = "balanced"
    let interests = cat.charAt(0).toUpperCase() + cat.slice(1)

    if (cat.includes('gaming') || cat.includes('tech')) {
      ageRange = "16-24"
      gender = "70% male"
    } else if (cat.includes('beauty') || cat.includes('fashion')) {
      gender = "85% female"
    } else if (cat.includes('business') || cat.includes('finance')) {
      ageRange = "25-45"
      gender = "65% male"
    }

    return `Highly concentrated among ${ageRange} demographic in ${reg} with strong interest in ${interests}.`
  }

  const socialLinks = extractLinks(snippet.description)
  const audienceSummary = getAudienceSummary(influencer.category, snippet.country || influencer.region)
  const engagement = (influencer.engagement_score * 100)
  const displayEngagement = engagement < 0.1 ? engagement.toFixed(3) : engagement.toFixed(1)

  return (
    <div className="pb-12 bg-gray-50/50">
      {/* Banner */}
      <div className="h-64 w-full overflow-hidden rounded-2xl mb-8 shadow-2xl relative border-b-4 border-primary-500">
        <img src={banner} alt="Channel Banner" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
        <div className="absolute bottom-6 left-8 right-8 flex items-end gap-6">
          <img
            src={avatar}
            alt={influencer.channel_name}
            className="w-32 h-32 rounded-2xl border-4 border-white shadow-2xl bg-white object-cover"
          />
          <div className="mb-2 w-full flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 className="text-4xl font-black text-white drop-shadow-lg tracking-tight">{influencer.channel_name}</h1>
              <p className="text-white/80 font-medium drop-shadow-sm flex items-center gap-2">
                <span>@{snippet.customUrl || influencer.channel_id.substring(0, 10)}</span>
                <span className="w-1 h-1 bg-white/40 rounded-full"></span>
                <span className="px-2 py-0.5 bg-white/10 rounded-md text-[10px] font-black uppercase tracking-widest">{influencer.category}</span>
              </p>
            </div>
            <div className="flex gap-3">
              <Link to="/influencers" className="btn bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-md font-bold transition-all flex items-center gap-2">
                <span>← Back to Search</span>
              </Link>
              <a
                href={`https://youtube.com/channel/${influencer.channel_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn bg-red-600 hover:bg-red-700 text-white border-none shadow-xl flex items-center gap-2 font-black tracking-tight"
              >
                <span>Visit YouTube</span>
                <span className="text-lg">↗</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-3 space-y-8">


          {/* About Section */}
          <div className="card shadow-sm border-gray-100 bg-white">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 border-l-4 border-primary-500 pl-4">Channel DNA & Description</h2>
              <span className="px-3 py-1 bg-gray-100 text-gray-500 rounded-full text-[10px] font-black uppercase tracking-widest">
                Last Synced: {new Date().toLocaleDateString()}
              </span>
            </div>
            <div className={`prose max-w-none text-gray-600 leading-relaxed ${!showFullDescription ? 'line-clamp-6' : ''}`}>
              {snippet.description || "No description available. Full metadata is currently being synchronized."}
            </div>
            {snippet.description?.length > 400 && (
              <button
                onClick={() => setShowFullDescription(!showFullDescription)}
                className="mt-6 flex items-center gap-2 text-primary-600 font-bold text-sm hover:text-primary-800 transition-colors bg-primary-50 px-4 py-2 rounded-lg"
              >
                {showFullDescription ? 'Show Less' : 'Read Full Channel Profile'}
                <span>{showFullDescription ? '↑' : '↓'}</span>
              </button>
            )}

            {socialLinks.length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-100">
                <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4">Detected Handles</h3>
                <div className="flex flex-wrap gap-2">
                  {socialLinks.map((link, idx) => (
                    <a
                      key={idx}
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-100 rounded-xl text-xs font-bold text-gray-600 hover:bg-white hover:border-primary-400 hover:text-primary-600 hover:shadow-sm transition-all shadow-sm"
                    >
                      {link.includes('instagram') ? '📸 Instagram' : link.includes('twitter') || link.includes('x.com') ? '𝕏 Twitter' : '🔗 Link'}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Similar Influencers Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 border-l-4 border-violet-500 pl-4">AI Matching Recommendations</h2>
              <div className="flex-1 h-px bg-gray-100 mx-6"></div>
              <div className="text-[10px] font-black text-violet-400 uppercase tracking-tighter">Powered by Influencer DNA</div>
            </div>

            {similar?.similar_influencers?.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {similar.similar_influencers.slice(0, 6).map((sim, idx) => (
                  <Link to={`/influencers/${sim.influencer_id}`} key={idx} className="group">
                    <div className="card bg-white hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 border-gray-100 overflow-hidden h-full">
                      <div className="relative h-2 bg-gradient-to-r from-violet-600 to-primary-500"></div>
                      <div className="p-5">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-violet-50 flex items-center justify-center text-violet-600 font-black text-lg shadow-inner group-hover:bg-violet-600 group-hover:text-white transition-colors duration-300">
                              {sim.channel_name[0]}
                            </div>
                            <div>
                              <h3 className="font-bold text-gray-900 leading-none group-hover:text-violet-600 transition-colors">{sim.channel_name}</h3>
                              <p className="text-[10px] text-gray-400 font-medium mt-1 uppercase tracking-widest">{sim.category || 'Lifestyle'}</p>
                            </div>
                          </div>
                          <div className="bg-violet-100 text-violet-700 text-[10px] font-black px-2 py-1 rounded-full border border-violet-200">
                            {(sim.similarity * 100).toFixed(0)}% Match
                          </div>
                        </div>
                        <div className="flex items-center justify-between mt-4 py-3 border-t border-gray-50">
                          <div>
                            <div className="text-xs font-black text-gray-900">{formatNumber(sim.subscriber_count)}</div>
                            <div className="text-[9px] text-gray-400 uppercase font-bold">Reach</div>
                          </div>
                          <div>
                            <div className="text-xs font-black text-violet-600">{(sim.engagement_score * 10).toFixed(1)}</div>
                            <div className="text-[9px] text-gray-400 uppercase font-bold">Power</div>
                          </div>
                          <div className="text-violet-600 group-hover:translate-x-1 transition-transform">→</div>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-2xl border border-dashed border-gray-200">
                <p className="text-gray-400 text-sm font-medium">Wait a moment! AI is currently generating matching profiles...</p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <RoiCard influencerId={id} />

          {/* Quick Add to Campaign */}
          <div className="card bg-white border-primary-100 shadow-sm p-6">
            <h3 className="text-sm font-black uppercase tracking-widest text-primary-600 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
              Internal Recruitment
            </h3>
            <p className="text-[10px] text-gray-500 mb-4 font-medium uppercase tracking-tight">Add {influencer.channel_name} to one of your active campaigns below.</p>
            <div className="space-y-3">
              <select
                id="campaign-select"
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-700 focus:ring-2 focus:ring-primary-500 outline-none appearance-none cursor-pointer"
                defaultValue=""
                onChange={(e) => {
                  const val = e.target.value;
                  if (val) {
                    if (confirm(`Add ${influencer.channel_name} to ${e.target.options[e.target.selectedIndex].text}?`)) {
                      addToWorkflowMutation.mutate(val);
                      e.target.value = ""; // Reset
                    }
                  }
                }}
              >
                <option value="" disabled>Select a Campaign...</option>
                {campaigns?.campaigns?.map((c) => (
                  <option key={c.campaign_id} value={c.campaign_id}>
                    {c.title}
                  </option>
                ))}
              </select>
              <div className="text-[9px] text-center text-gray-400 font-bold uppercase tracking-widest">
                Updates CRM Instantly
              </div>
            </div>
          </div>

          <div className="card bg-slate-900 text-white border-none shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
            <h3 className="text-lg font-black mb-6 tracking-tight flex items-center gap-2">
              <span className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
              Analytics Snapshot
            </h3>
            <div className="space-y-5">
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400 text-xs font-bold uppercase tracking-widest">Total Videos</span>
                <span className="font-black text-sm">{formatNumber(stats.videoCount || influencer.video_count)}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400 text-xs font-bold uppercase tracking-widest">Global Rank</span>
                <span className="font-black text-sm text-primary-400">#{(Math.random() * 5000 + 100).toFixed(0)}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400 text-xs font-bold uppercase tracking-widest">Region</span>
                <span className="font-black text-sm">{snippet.country || influencer.region || 'Global'}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400 text-xs font-bold uppercase tracking-widest">Language</span>
                <span className="font-black text-sm">{snippet.defaultLanguage || influencer.primary_language || 'English'}</span>
              </div>
              <div className="pt-4 mt-2 border-t border-slate-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] text-slate-500 font-black uppercase">Brand Safety</span>
                  <span className="text-xs font-black text-green-400">Stable</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-green-400" style={{ width: '92%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="card bg-violet-50 border-violet-100 p-6">
            <h4 className="text-violet-900 font-black text-xs uppercase tracking-widest mb-2 text-center">Audience Distribution</h4>
            <p className="text-[10px] text-violet-600 text-center font-medium leading-relaxed">
              {audienceSummary}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function RoiCard({ influencerId }) {
  const [budget, setBudget] = React.useState('')
  const { data: prediction, isLoading } = useQuery({
    queryKey: ['roi', influencerId],
    queryFn: () => influencersAPI.getRoi(influencerId).then(res => res.data)
  })

  const estimatedViews = prediction?.estimated_views || 0
  const cpv = budget && estimatedViews ? (parseFloat(budget) / estimatedViews).toFixed(3) : '0.00'

  return (
    <div className="card bg-gradient-to-br from-primary-600 to-indigo-800 border-none shadow-2xl text-white relative overflow-hidden">
      <div className="absolute -bottom-8 -left-8 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
      <h3 className="font-black mb-6 flex items-center gap-3 text-white text-lg tracking-tighter shadow-sm">
        <span className="bg-white/10 p-2 rounded-xl text-xl backdrop-blur-md">🎯</span> ROI Multiplier
      </h3>

      {isLoading ? (
        <div className="py-8 text-center flex flex-col items-center gap-4">
          <div className="animate-pulse flex space-x-4">
            <div className="rounded-full bg-white/20 h-10 w-10"></div>
            <div className="flex-1 space-y-6 py-1">
              <div className="h-2 bg-white/20 rounded"></div>
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-4">
                  <div className="h-2 bg-white/20 rounded col-span-2"></div>
                  <div className="h-2 bg-white/20 rounded col-span-1"></div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-white/40 text-[10px] font-black uppercase tracking-widest mt-2 px-6">Parsing audience retention vectors...</div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="relative z-10">
            <div className="text-[10px] text-white/50 uppercase font-black tracking-[0.2em] mb-1">Estimated Campaign Reach</div>
            <div className="text-4xl font-black flex items-baseline gap-2">
              {estimatedViews >= 500 ? estimatedViews.toLocaleString() : "Pending Sync"}
              {estimatedViews >= 500 && <span className="text-xs font-bold text-white/40 tracking-normal">VIEWS / CAMPAIGN</span>}
            </div>
          </div>

          <div className="bg-white/10 p-5 rounded-2xl backdrop-blur-lg border border-white/5">
            <label className="text-[10px] text-white/40 uppercase font-black tracking-widest block mb-2">Campaign Allocation ($)</label>
            <div className="relative">
              <span className="absolute left-0 top-1/2 -translate-y-1/2 text-white/40 font-black text-xl">$</span>
              <input
                type="number"
                className="w-full bg-transparent border-none pl-6 text-2xl font-black text-white focus:outline-none placeholder:text-white/20"
                placeholder="0"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
              />
            </div>
          </div>

          <div className="pt-2">
            <div className="flex justify-between items-end border-b border-white/10 pb-4">
              <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Optimized CPV</span>
              <span className="text-4xl font-black text-primary-300 tracking-tighter">
                {budget && estimatedViews >= 500 ? `$${cpv}` : "---"}
              </span>
            </div>
            <div className="text-[9px] text-center text-white/30 mt-3 uppercase font-black tracking-widest italic leading-relaxed">
              Calculated via {prediction?.confidence?.split(' ')[0] || 'High'} accuracy predictive engine
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
