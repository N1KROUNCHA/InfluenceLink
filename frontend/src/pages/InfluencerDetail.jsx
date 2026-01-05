import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { influencersAPI } from '../services/api'

export default function InfluencerDetail() {
  const { id } = useParams()

  const { data: influencer, isLoading } = useQuery({
    queryKey: ['influencer', id],
    queryFn: () => influencersAPI.get(id).then(res => res.data)
  })

  // Hook must be at top level, use 'enabled' to conditionally run
  const { data: similar } = useQuery({
    queryKey: ['similar-influencers', influencer?.channel_id],
    queryFn: () => influencersAPI.findSimilar(influencer.channel_id).then(res => res.data),
    enabled: !!influencer?.channel_id
  })

  if (isLoading) {
    return <div className="card text-center py-8">Loading...</div>
  }

  if (!influencer) {
    return <div className="card text-center py-8">Influencer not found</div>
  }

  return (
    <div>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{influencer.channel_name}</h1>
          <p className="mt-2 text-gray-600">Influencer ID: {id}</p>
        </div>
        <Link to="/influencers" className="btn btn-secondary">
          ← Back to Influencers
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Profile Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-500">Channel ID</div>
                <div className="mt-1 font-mono text-sm">{influencer.channel_id}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Category</div>
                <div className="mt-1 font-medium">{influencer.category}</div>
              </div>
              {influencer.subscriber_count && (
                <div>
                  <div className="text-sm text-gray-500">Subscribers</div>
                  <div className="mt-1 font-medium text-lg">
                    {influencer.subscriber_count.toLocaleString()}
                  </div>
                </div>
              )}
              {influencer.engagement_score && (
                <div>
                  <div className="text-sm text-gray-500">Engagement Score</div>
                  <div className="mt-1 font-medium text-lg text-primary-600">
                    {(influencer.engagement_score * 100).toFixed(1)}%
                  </div>
                </div>
              )}
              {influencer.brand_safety_score && (
                <div>
                  <div className="text-sm text-gray-500">Brand Safety Score</div>
                  <div className={`mt-1 font-medium text-lg ${influencer.brand_safety_score > 0.8 ? 'text-green-600' :
                    influencer.brand_safety_score > 0.6 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                    {(influencer.brand_safety_score * 100).toFixed(1)}%
                  </div>
                </div>
              )}
            </div>
          </div>

          {influencer.dna && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">DNA Profile</h2>
              {influencer.dna.topics && influencer.dna.topics.length > 0 && (
                <div className="mb-4">
                  <div className="text-sm text-gray-500 mb-2">Topics</div>
                  <div className="flex flex-wrap gap-2">
                    {influencer.dna.topics.map((topic, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {influencer.dna.style && (
                <div>
                  <div className="text-sm text-gray-500 mb-2">Style</div>
                  <div className="font-medium">{influencer.dna.style}</div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold mb-3">Quick Stats</h3>
            <div className="space-y-3">
              {influencer.subscriber_count && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Subscribers</span>
                  <span className="font-semibold">
                    {influencer.subscriber_count.toLocaleString()}
                  </span>
                </div>
              )}
              {influencer.engagement_score && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Engagement</span>
                  <span className="font-semibold text-primary-600">
                    {(influencer.engagement_score * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          <RoiCard influencerId={id} />

        </div>
      </div>

      {/* Similar Influencers Section */}
      {
        similar?.similar_influencers?.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Similar Influencers</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {similar.similar_influencers.map((sim, idx) => (
                <div key={idx} className="card hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-gray-900 truncate">{sim.channel_name}</h3>
                    <span className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full">
                      {((sim.similarity_score || 0) * 100).toFixed(0)}% Match
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    {sim.channel_id}
                  </div>
                  <div className="space-y-1">
                    {sim.topics && (
                      <div className="flex flex-wrap gap-1">
                        {sim.topics.slice(0, 3).map((t, i) => (
                          <span key={i} className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <Link to={`/influencers/channel/${sim.channel_id}`} className="text-primary-600 hover:text-primary-800 text-sm font-medium">
                      View Channel →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      }
    </div >
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
    <div className="card bg-gradient-to-br from-violet-50 to-purple-50 border-violet-100">
      <h3 className="font-semibold mb-3 flex items-center gap-2 text-violet-900">
        <span>🚀</span> AI Performance Predictor
      </h3>

      {isLoading ? (
        <div className="text-sm text-gray-500">Analyze performance...</div>
      ) : (
        <div className="space-y-4">
          <div>
            <div className="text-xs text-gray-500 uppercase font-semibold">Estimated Views</div>
            <div className="text-2xl font-bold text-violet-700">
              {estimatedViews.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Confidence: <span className="text-green-600 font-medium">{prediction?.confidence}</span>
            </div>
          </div>

          <div>
            <label className="label text-xs">Campaign Budget ($)</label>
            <input
              type="number"
              className="input bg-white"
              placeholder="Enter budget..."
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
          </div>

          <div className="pt-3 border-t border-violet-200">
            <div className="flex justify-between items-end">
              <span className="text-sm font-medium text-gray-600">Effective CPV</span>
              <span className="text-xl font-bold text-gray-900">${cpv}</span>
            </div>
            <div className="text-xs text-right text-gray-500">Cost per View</div>
          </div>
        </div>
      )}
    </div>
  )
}

