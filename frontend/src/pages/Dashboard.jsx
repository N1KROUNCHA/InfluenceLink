import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { campaignsAPI, healthAPI } from '../services/api'

export default function Dashboard() {
  const { data: campaigns, isLoading: campaignsLoading, error: campaignsError } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsAPI.list().then(res => res.data),
    retry: false,
    onError: (error) => {
      console.error('Campaigns API error:', error)
    }
  })

  const { data: health, error: healthError } = useQuery({
    queryKey: ['health'],
    queryFn: () => healthAPI.detailed().then(res => res.data),
    refetchInterval: 30000,
    retry: false,
    onError: (error) => {
      console.error('Health API error:', error)
    }
  })

  const activeCampaigns = campaigns?.campaigns?.filter(c => c.status === 'active') || []
  const completedCampaigns = campaigns?.campaigns?.filter(c => c.status === 'completed') || []

  // Show error if API is not available
  if (campaignsError || healthError) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <h2 className="text-xl font-bold text-red-600 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">
            Could not connect to the API. Make sure your backend is running at http://127.0.0.1:8000
          </p>
          <p className="text-sm text-gray-500">
            Error: {campaignsError?.message || healthError?.message || 'Unknown error'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your influencer marketing campaigns</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card card-hover">
          <div className="text-sm font-medium text-gray-500">Total Campaigns</div>
          <div className="mt-2 text-4xl font-bold text-gray-900">
            {campaignsLoading ? '...' : campaigns?.count || 0}
          </div>
        </div>

        <div className="card card-hover">
          <div className="text-sm font-medium text-gray-500">Active Campaigns</div>
          <div className="mt-2 text-4xl font-bold text-emerald-600">
            {campaignsLoading ? '...' : activeCampaigns.length}
          </div>
        </div>

        <div className="card card-hover">
          <div className="text-sm font-medium text-gray-500">Completed</div>
          <div className="mt-2 text-4xl font-bold text-blue-600">
            {campaignsLoading ? '...' : completedCampaigns.length}
          </div>
        </div>

        <div className="card card-hover">
          <div className="text-sm font-medium text-gray-500">System Status</div>
          <div className="mt-3">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${health?.status === 'healthy'
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-red-100 text-red-700'
              }`}>
              <span className={`w-2 h-2 mr-2 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-red-500'
                }`}></span>
              {health?.status || 'Checking...'}
            </span>
          </div>
        </div>
      </div>

      {/* Recent Campaigns */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Recent Campaigns</h2>
          <Link to="/campaigns/create" className="btn btn-primary shadow-lg hover:shadow-violet-500/30">
            + Create Campaign
          </Link>
        </div>

        {campaignsLoading ? (
          <div className="text-center py-12 text-gray-500 animate-pulse">Loading campaigns...</div>
        ) : campaigns?.campaigns?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50/50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider rounded-l-xl">Title</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Budget</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider rounded-r-xl">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {campaigns.campaigns.slice(0, 5).map((campaign) => (
                  <tr key={campaign.campaign_id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {campaign.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {campaign.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full ${campaign.status === 'active' ? 'bg-emerald-100 text-emerald-700' :
                          campaign.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                        }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      ${campaign.budget?.toLocaleString() || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link to={`/campaigns/${campaign.campaign_id}`} className="text-violet-600 hover:text-violet-800 font-semibold hover:underline">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-16 bg-gray-50/50 rounded-xl border-2 border-dashed border-gray-200">
            <p className="text-gray-500 mb-4">No campaigns found. Start by creating one!</p>
            <Link to="/campaigns/create" className="btn btn-secondary">Create Campaign</Link>
          </div>
        )}
      </div>
    </div>
  )
}

