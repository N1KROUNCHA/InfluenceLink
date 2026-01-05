import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { campaignsAPI } from '../services/api'

export default function CampaignDetail() {
  const { id } = useParams()

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

  const statusMutation = useMutation({
    mutationFn: (status) => campaignsAPI.updateStatus(id, status),
    onSuccess: () => {
      refetch()
      alert('Status updated successfully!')
    },
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
                  <select
                    value={campaignData.status}
                    onChange={(e) => statusMutation.mutate(e.target.value)}
                    className="input w-auto"
                  >
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                  </select>
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

          {/* Recommendations */}
          {recommendations && (
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Top Recommendations</h2>
                <span className="text-sm text-gray-500">
                  {recommendations.recommendations?.length || 0} influencers
                </span>
              </div>
              {recommendations.recommendations?.length > 0 ? (
                <div className="space-y-3">
                  {recommendations.recommendations.map((rec, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold text-gray-900">{rec.channel_name}</div>
                          <div className="text-sm text-gray-500 mt-1">{rec.channel_id}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-primary-600">
                            Score: {(rec.score * 100).toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-500">
                            Confidence: {(rec.confidence * 100).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                      {rec.why_recommended && (
                        <div className="mt-2 text-sm text-gray-600">{rec.why_recommended}</div>
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
        </div>

        {/* Stats Sidebar */}
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
      </div>
    </div>
  )
}

