import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { campaignsAPI } from '../services/api'

export default function Campaigns() {
  const [statusFilter, setStatusFilter] = useState('')
  
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['campaigns', statusFilter],
    queryFn: () => campaignsAPI.list(statusFilter || null).then(res => res.data)
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Campaigns</h1>
          <p className="mt-2 text-gray-600">Manage your influencer marketing campaigns</p>
        </div>
        <Link to="/campaigns/create" className="btn btn-primary">
          + Create Campaign
        </Link>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex gap-4 items-center">
          <label className="label mb-0">Filter by Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input w-auto"
          >
            <option value="">All</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
          <div className="ml-auto text-sm text-gray-500">
            {data?.count || 0} campaigns found
          </div>
        </div>
      </div>

      {/* Campaigns List */}
      {isLoading ? (
        <div className="card text-center py-8">Loading...</div>
      ) : data?.campaigns?.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.campaigns.map((campaign) => (
            <div key={campaign.campaign_id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{campaign.title}</h3>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  campaign.status === 'active' ? 'bg-green-100 text-green-800' :
                  campaign.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {campaign.status}
                </span>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="text-sm text-gray-600">
                  <span className="font-medium">Category:</span> {campaign.category}
                </div>
                {campaign.budget && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Budget:</span> ${campaign.budget}
                  </div>
                )}
                {campaign.created_at && (
                  <div className="text-sm text-gray-500">
                    Created: {new Date(campaign.created_at).toLocaleDateString()}
                  </div>
                )}
              </div>
              
              <div className="flex gap-2">
                <Link
                  to={`/campaigns/${campaign.campaign_id}`}
                  className="btn btn-primary flex-1 text-center"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">No campaigns found</p>
          <Link to="/campaigns/create" className="btn btn-primary">
            Create Your First Campaign
          </Link>
        </div>
      )}
    </div>
  )
}

