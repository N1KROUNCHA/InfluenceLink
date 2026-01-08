import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { campaignsAPI, workflowAPI, contentAPI } from '../services/api'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function CampaignDetail() {
  const { id } = useParams()
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isBrand = user.type === 'brand'
  const [activeTab, setActiveTab] = useState('recommendations')

  const { data: campaign, isLoading, refetch } = useQuery({
    queryKey: ['campaign', id],
    queryFn: () => campaignsAPI.get(id).then(res => res.data)
  })

  const { data: stats } = useQuery({
    queryKey: ['campaign-stats', id],
    queryFn: () => campaignsAPI.getStats(id).then(res => res.data),
    enabled: !!campaign
  })

  const { data: recommendations } = useQuery({
    queryKey: ['campaign-recommendations', id],
    queryFn: () => campaignsAPI.getRecommendations(id).then(res => res.data),
    enabled: !!campaign
  })

  const { data: workflow, refetch: refetchWorkflow } = useQuery({
    queryKey: ['campaign-workflow', id],
    queryFn: () => workflowAPI.get(id).then(res => res.data),
    enabled: !!campaign
  })

  // Influencer specific queries
  const { data: contentHistory, refetch: refetchHistory } = useQuery({
    queryKey: ['creator-history', id],
    queryFn: () => contentAPI.getCreatorHistory(user.id, id).then(res => res.data),
    enabled: !!user.id && !isBrand
  })

  const statusMutation = useMutation({
    mutationFn: (status) => campaignsAPI.updateStatus(id, status),
    onSuccess: () => {
      refetch()
      alert('Status updated successfully!')
    },
  })

  const addToWorkflowMutation = useMutation({
    mutationFn: (influencerId) => workflowAPI.add(id, influencerId),
    onSuccess: () => {
      refetchWorkflow()
      alert('Added to workflow!')
    }
  })

  const queryClient = useQueryClient()

  // ... existing queries ...

  const updateWorkflowMutation = useMutation({
    mutationFn: ({ influencer_id, status, notes }) => workflowAPI.update(id, influencer_id, { status, notes }),
    onSuccess: () => {
      refetchWorkflow()
      queryClient.invalidateQueries({ queryKey: ['influencer-collaborations'] })
    }
  })

  const removeFromWorkflowMutation = useMutation({
    mutationFn: (influencerId) => workflowAPI.remove(id, influencerId),
    onSuccess: () => refetchWorkflow()
  })

  if (isLoading) {
    return <div className="card text-center py-8">Loading...</div>
  }

  if (!campaign) {
    return <div className="card text-center py-8">Campaign not found</div>
  }

  const campaignData = campaign.campaign || campaign

  return (
    <div>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{campaignData.title}</h1>
          <p className="mt-2 text-gray-600">Campaign ID: {id}</p>
        </div>
        <Link to="/campaigns" className="btn btn-secondary">
          ← Back to Campaigns
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Campaign Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Campaign Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500">Status</div>
                <div className="mt-1">
                  {isBrand ? (
                    <select
                      value={campaignData.status}
                      onChange={(e) => statusMutation.mutate(e.target.value)}
                      className="input w-auto"
                    >
                      <option value="draft">Draft</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                    </select>
                  ) : (
                    <span className="capitalize font-black text-violet-600">{campaignData.status}</span>
                  )}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Category</div>
                <div className="mt-1 font-medium">{campaignData.category}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Budget</div>
                <div className="mt-1 font-medium">${campaignData.budget || 'N/A'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Target Region</div>
                <div className="mt-1 font-medium">{campaignData.target_region}</div>
              </div>
              {campaignData.target_language && (
                <div>
                  <div className="text-sm text-gray-500">Target Language</div>
                  <div className="mt-1 font-medium">{campaignData.target_language}</div>
                </div>
              )}
              {campaignData.required_style && (
                <div>
                  <div className="text-sm text-gray-500">Required Style</div>
                  <div className="mt-1 font-medium">{campaignData.required_style}</div>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="flex border-b border-gray-200 mb-6">
              {isBrand ? (
                <>
                  <button
                    onClick={() => setActiveTab('recommendations')}
                    className={`pb-3 px-4 font-medium transition-colors ${activeTab === 'recommendations' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
                  >
                    AI Recommendations
                  </button>
                  <button
                    onClick={() => setActiveTab('workflow')}
                    className={`pb-3 px-4 font-medium transition-colors ${activeTab === 'workflow' ? 'text-primary-600 border-b-2 border-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
                  >
                    Workflow Tracker (CRM)
                  </button>
                </>
              ) : (
                <button
                  className="pb-3 px-4 font-medium text-primary-600 border-b-2 border-primary-600"
                >
                  My Collaboration
                </button>
              )}
            </div>

            {isBrand && (
              <>
                {activeTab === 'recommendations' && recommendations && (
                  <div>
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-xl font-bold">Top AI Matches</h2>
                      <span className="text-sm text-gray-500">
                        {recommendations.recommendations?.length || 0} influencers
                      </span>
                    </div>
                    {recommendations.recommendations?.length > 0 ? (
                      <div className="space-y-3">
                        {recommendations.recommendations.map((rec, idx) => (
                          <div key={idx} className="group border border-gray-100 rounded-xl p-4 transition-all hover:border-violet-200 hover:bg-violet-50/30">
                            <div className="flex justify-between items-start">
                              <Link to={`/influencers/${rec.influencer_id}`} className="flex-1">
                                <div className="font-bold text-gray-900 group-hover:text-primary-600">{rec.channel_name}</div>
                                <div className="text-sm text-gray-500 mt-1">{rec.channel_id}</div>
                              </Link>
                              <div className="text-right flex items-start gap-4">
                                <div>
                                  <div className="text-sm font-black text-primary-600">
                                    Score: {(rec.score * 100).toFixed(1)}%
                                  </div>
                                  <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">
                                    Confidence: {(rec.confidence * 100).toFixed(0)}%
                                  </div>
                                </div>
                                {workflow?.all_ids?.includes(rec.influencer_id) ? (
                                  <span className="text-[10px] font-black text-green-600 bg-green-50 px-2 py-1 rounded-md border border-green-100 uppercase tracking-widest">
                                    In Workflow
                                  </span>
                                ) : (
                                  <button
                                    onClick={() => addToWorkflowMutation.mutate(rec.influencer_id)}
                                    className="btn btn-secondary btn-sm bg-white border-gray-200 hover:bg-primary-600 hover:text-white hover:border-primary-600 group-hover:shadow-sm"
                                  >
                                    Add to Workflow
                                  </button>
                                )}
                              </div>
                            </div>
                            {rec.why_recommended && (
                              <div className="mt-3 text-sm text-gray-600 border-t border-gray-100 pt-2 italic">
                                "{rec.why_recommended}"
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        No recommendations yet. Rankings are being processed.
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'workflow' && workflow?.pipeline && (
                  <div className="space-y-8">
                    {Object.entries(workflow.pipeline).map(([stage, influencers]) => (
                      <div key={stage} className="space-y-4">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-bold uppercase tracking-wider text-gray-700">
                            {stage.replace('_', ' ')}
                          </h3>
                          <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full font-bold">
                            {influencers.length}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {influencers.length > 0 ? influencers.map((inf) => (
                            <div key={inf.influencer_id} className="card bg-gray-50 border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
                              <div className="flex justify-between items-start mb-3">
                                <Link to={`/influencers/${inf.influencer_id}`} className="font-bold text-gray-900 hover:text-primary-600">
                                  {inf.channel_name}
                                </Link>
                                <button
                                  onClick={() => { if (confirm("Remove from workflow?")) removeFromWorkflowMutation.mutate(inf.influencer_id) }}
                                  className="text-gray-400 hover:text-red-500"
                                >
                                  ×
                                </button>
                              </div>

                              <div className="mb-4">
                                <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Collaboration Notes</div>
                                <textarea
                                  defaultValue={inf.notes || ""}
                                  onBlur={(e) => updateWorkflowMutation.mutate({ influencer_id: inf.influencer_id, status: stage, notes: e.target.value })}
                                  className="text-xs text-gray-600 bg-white border border-transparent hover:border-gray-200 focus:border-primary-400 focus:ring-0 w-full rounded-md p-2 transition-all resize-none min-h-[60px]"
                                  placeholder="Add private notes here (e.g., agreed price, content ideas)..."
                                />
                              </div>

                              <div className="flex flex-wrap gap-2">
                                {stage !== 'outreached' && (
                                  <button
                                    onClick={() => updateWorkflowMutation.mutate({ influencer_id: inf.influencer_id, status: 'outreached' })}
                                    className="text-[10px] px-2 py-1 border border-blue-200 text-blue-600 rounded-md hover:bg-blue-600 hover:text-white transition-colors uppercase font-bold"
                                  >
                                    Mark Outreached
                                  </button>
                                )}
                                {stage !== 'negotiating' && (
                                  <button
                                    onClick={() => updateWorkflowMutation.mutate({ influencer_id: inf.influencer_id, status: 'negotiating' })}
                                    className="text-[10px] px-2 py-1 border border-yellow-200 text-yellow-600 rounded-md hover:bg-yellow-600 hover:text-white transition-colors uppercase font-bold"
                                  >
                                    Negotiating
                                  </button>
                                )}
                                {stage !== 'contracted' && (
                                  <button
                                    onClick={() => updateWorkflowMutation.mutate({ influencer_id: inf.influencer_id, status: 'contracted' })}
                                    className="text-[10px] px-2 py-1 border border-green-200 text-green-600 rounded-md hover:bg-green-600 hover:text-white transition-colors uppercase font-bold"
                                  >
                                    Sign Contract
                                  </button>
                                )}
                                {stage !== 'post_live' && (
                                  <button
                                    onClick={() => updateWorkflowMutation.mutate({ influencer_id: inf.influencer_id, status: 'post_live' })}
                                    className="text-[10px] px-2 py-1 border border-purple-200 text-purple-600 rounded-md hover:bg-purple-600 hover:text-white transition-colors uppercase font-bold"
                                  >
                                    Mark Post Live
                                  </button>
                                )}
                                {stage !== 'rejected' && (
                                  <button
                                    onClick={() => { if (confirm("Reject this influencer?")) updateWorkflowMutation.mutate({ influencer_id: inf.influencer_id, status: 'rejected' }) }}
                                    className="text-[10px] px-2 py-1 border border-red-200 text-red-600 rounded-md hover:bg-red-600 hover:text-white transition-colors uppercase font-bold"
                                  >
                                    Reject
                                  </button>
                                )}
                              </div>
                            </div>
                          )) : (
                            <div className="md:col-span-2 border-2 border-dashed border-gray-200 rounded-xl py-6 text-center text-gray-400 text-sm italic">
                              No creators in this stage
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            {!isBrand && (
              <div className="space-y-6">
                {/* ... existing Insight card ... */}
                <div className="bg-violet-50 p-8 rounded-2xl border-2 border-violet-100 italic">
                  <h3 className="text-lg font-bold text-violet-800 mb-4 not-italic flex items-center gap-2">
                    <span className="text-2xl">🤝</span> Collaboration Insights
                  </h3>
                  <p className="text-violet-700 leading-relaxed font-medium">
                    You are currently in the <b className="text-violet-900 uppercase tracking-wider">{workflow?.pipeline ? Object.entries(workflow.pipeline).find(([_, influencers]) => influencers.find(inf => inf.influencer_id === user.id))?.[0]?.replace('_', ' ') || 'discovery' : 'loading...'}</b> stage of this campaign.
                  </p>
                  <div className="mt-6 p-6 bg-white rounded-xl shadow-sm border border-violet-100 not-italic">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-violet-600"></div>
                      <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">Brand Briefing & Instructions</span>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed bg-gray-50 p-4 rounded-lg border border-gray-50">
                      "{workflow?.pipeline ? Object.values(workflow.pipeline).flat().find(inf => inf.influencer_id === user.id)?.notes || "The brand hasn't added specific notes for you yet. They typically share content guidelines and creative directions here once you move past discovery." : "..."}"
                    </p>
                  </div>
                  <div className="mt-8 flex items-center justify-between text-[10px] font-black uppercase tracking-[0.2em] text-violet-400">
                    <span>Generated by InfluenceLink AI</span>
                    <span className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                      Active Collaboration
                    </span>
                  </div>
                </div>

                {/* Quick Actions for Influencer */}
                <div className="card border border-violet-100 bg-white shadow-lg shadow-violet-100/20">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <Link
                      to={`/creator-studio?campaignId=${id}`}
                      className="flex-1 btn bg-violet-600 text-white hover:bg-violet-700 font-bold py-3 flex items-center justify-center gap-2"
                    >
                      <span>✨</span> Content Ideation Studio
                    </Link>

                    {workflow?.pipeline && (() => {
                      const myStatus = Object.entries(workflow.pipeline).find(([_, influencers]) => influencers.find(inf => inf.influencer_id === user.id))?.[0]
                      if (myStatus && myStatus !== 'completed') {
                        return (
                          <button
                            onClick={() => {
                              if (confirm("Confirm to mark this collaboration as completed?")) {
                                updateWorkflowMutation.mutate({ influencer_id: user.id, status: 'completed' })
                              }
                            }}
                            className="flex-1 btn bg-emerald-500 text-white hover:bg-emerald-600 font-bold py-3"
                          >
                            Mark as Completed ✓
                          </button>
                        )
                      }
                      return null
                    })()}
                  </div>
                </div>

                {/* Content History */}
                <div className="card border-gray-100">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-bold text-gray-900">Creation History</h3>
                    <button onClick={() => refetchHistory()} className="text-sm text-violet-600 font-bold hover:underline">Refresh</button>
                  </div>

                  {contentHistory && contentHistory.length > 0 ? (
                    <div className="space-y-4">
                      {contentHistory.map((item, idx) => (
                        <div key={idx} className="bg-gray-50 rounded-xl p-5 border border-gray-100 hover:border-violet-200 transition-colors">
                          <div className="flex justify-between items-start mb-3">
                            <div className="text-[10px] font-black uppercase tracking-widest text-gray-400">
                              {new Date(item.generated_at).toLocaleString()}
                            </div>
                            <span className="bg-violet-100 text-violet-700 text-[9px] font-black px-2 py-0.5 rounded-full uppercase">AI Draft</span>
                          </div>
                          <div className="prose prose-sm max-w-none text-gray-600">
                            {(item.content || "").substring(0, 150)}...
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 border-2 border-dashed border-gray-100 rounded-xl">
                      <div className="text-2xl mb-2">📜</div>
                      <p className="text-sm text-gray-500 font-medium">No saved content yet.</p>
                      <Link to={`/creator-studio?campaignId=${id}`} className="text-xs font-black text-violet-600 hover:underline mt-2 inline-block">Start Creating ↗</Link>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {isBrand && (
          <div className="space-y-6">
            {stats && (
              <div className="card">
                <h2 className="text-xl font-bold mb-4">Statistics</h2>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-gray-500">Total Recommendations</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {stats.statistics?.total_recommendations || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Average Score</div>
                    <div className="text-2xl font-bold text-primary-600">
                      {((stats.statistics?.average_score || 0) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Max Score</div>
                    <div className="text-xl font-semibold text-green-600">
                      {((stats.statistics?.max_score || 0) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Average Confidence</div>
                    <div className="text-xl font-semibold text-blue-600">
                      {((stats.statistics?.average_confidence || 0) * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="card">
              <h3 className="font-semibold mb-3">Quick Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    if (confirm("This can take 2-10 minutes. Start now?")) {
                      campaignsAPI.rerank(id)
                        .then(() => alert("Ranking started! Check back in a few minutes."))
                        .catch(err => alert("Failed to start: " + err.message))
                    }
                  }}
                  className="btn btn-primary w-full shadow-lg hover:shadow-violet-500/30 bg-gradient-to-r from-violet-600 to-fuchsia-600"
                >
                  Available Influencers (Rank)
                </button>

                <Link
                  to={`/content/${id}`}
                  className="btn btn-secondary w-full text-center"
                >
                  Generate Content
                </Link>
                <button
                  onClick={() => refetch()}
                  className="btn btn-secondary w-full"
                >
                  Refresh Data
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

