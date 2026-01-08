import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { influencersAPI } from '../services/api'

export default function Influencers() {
  // Form state (inputs)
  const [filters, setFilters] = useState({
    category: '',
    min_subscribers: '',
    max_subscribers: '',
    min_engagement: '',
    limit: 50,
  })

  // Query state (what is actually sent to API)
  const [activeFilters, setActiveFilters] = useState(filters)

  const { data, isLoading } = useQuery({
    queryKey: ['influencers-search', activeFilters],
    queryFn: () => influencersAPI.search(activeFilters).then(res => res.data),
    enabled: true
  })

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.name === 'limit' ? parseInt(e.target.value) || 20 : e.target.value,
    })
  }

  const handleSearch = () => {
    setActiveFilters(filters)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Influencers</h1>
        <p className="mt-2 text-gray-600">Search and discover influencers for your campaigns</p>
      </div>

      {/* Search Filters */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold mb-4">Search Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="label">Category</label>
            <input
              type="text"
              name="category"
              value={filters.category}
              onChange={handleFilterChange}
              onKeyDown={handleKeyDown}
              className="input"
              placeholder="e.g., Tech, Beauty"
            />
          </div>

          <div>
            <label className="label">Min Subscribers</label>
            <input
              type="number"
              name="min_subscribers"
              value={filters.min_subscribers}
              onChange={handleFilterChange}
              onKeyDown={handleKeyDown}
              className="input"
              placeholder="10000"
            />
          </div>

          <div>
            <label className="label">Max Subscribers</label>
            <input
              type="number"
              name="max_subscribers"
              value={filters.max_subscribers}
              onChange={handleFilterChange}
              onKeyDown={handleKeyDown}
              className="input"
              placeholder="1000000"
            />
          </div>

          <div>
            <label className="label">Min Engagement</label>
            <input
              type="number"
              name="min_engagement"
              value={filters.min_engagement}
              onChange={handleFilterChange}
              onKeyDown={handleKeyDown}
              className="input"
              placeholder="0.2"
              step="0.1"
            />
          </div>

          <div>
            <label className="label">Limit</label>
            <input
              type="number"
              name="limit"
              value={filters.limit}
              onChange={handleFilterChange}
              onKeyDown={handleKeyDown}
              className="input"
              min="1"
              max="100"
            />
          </div>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <button
            onClick={handleSearch}
            className="btn btn-primary shadow-lg hover:shadow-violet-500/30"
          >
            Search
          </button>
          <div className="text-sm text-gray-500">
            {data?.count || 0} influencers found
          </div>
        </div>
      </div>

      {/* Influencers List */}
      {isLoading ? (
        <div className="card text-center py-8">Loading...</div>
      ) : data?.influencers?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.influencers.map((influencer) => (
            <div key={influencer.influencer_id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  {influencer.thumbnails?.default?.url ? (
                    <img
                      src={influencer.thumbnails.default.url}
                      alt={influencer.channel_name}
                      className="w-12 h-12 rounded-full border border-gray-100 shadow-sm object-cover"
                    />
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">
                      {influencer.channel_name[0]}
                    </div>
                  )}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 leading-tight">{influencer.channel_name}</h3>
                    <div className="text-xs text-gray-400 font-mono mt-0.5">{influencer.channel_id.substring(0, 12)}...</div>
                  </div>
                </div>
                {influencer.brand_safety_score && (
                  <span className={`px-2 py-1 text-[10px] font-black uppercase tracking-tight rounded-md ${influencer.brand_safety_score > 0.8 ? 'bg-green-100 text-green-800' :
                    influencer.brand_safety_score > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                    Safe: {(influencer.brand_safety_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>

              <div className="space-y-2 mb-4">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Category:</span> {influencer.category}
                </div>
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Subscribers:</span> {influencer.subscriber_count?.toLocaleString() || 'N/A'}
                </div>
                {influencer.engagement_score && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Engagement:</span> {(influencer.engagement_score * 100).toFixed(1)}%
                  </div>
                )}
                <div className="text-xs text-gray-500 font-mono">
                  {influencer.channel_id}
                </div>
              </div>

              <Link
                to={`/influencers/${influencer.influencer_id}`}
                className="btn btn-primary w-full text-center"
              >
                View Details
              </Link>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No influencers found. Try adjusting your filters.</p>
        </div>
      )}
    </div>
  )
}

