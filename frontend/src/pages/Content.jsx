import { useParams, Link } from 'react-router-dom'
import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { contentAPI, campaignsAPI } from '../services/api'

export default function Content() {
  const { campaignId } = useParams()
  const [showHistory, setShowHistory] = useState(false)

  const { data: campaign } = useQuery({
    queryKey: ['campaign', campaignId],
    queryFn: () => campaignsAPI.get(campaignId).then(res => res.data)
  })

  const generateMutation = useMutation({
    mutationFn: () => contentAPI.generate(campaignId),
    onSuccess: () => {
      alert('Content generated successfully!')
      refetchHistory()
    },
    onError: (error) => {
      alert('Error generating content: ' + (error.response?.data?.content || error.message))
    },
  })

  const { data: history, refetch: refetchHistory } = useQuery({
    queryKey: ['content-history', campaignId],
    queryFn: () => contentAPI.getHistory(campaignId).then(res => res.data),
    enabled: showHistory
  })

  const { data: latest } = useQuery({
    queryKey: ['content-latest', campaignId],
    queryFn: () => contentAPI.getLatest(campaignId).then(res => res.data),
    enabled: !showHistory
  })

  const content = showHistory ? null : latest

  return (
    <div>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Content Generation</h1>
          <p className="mt-2 text-gray-600">
            Campaign: {campaign?.campaign?.title || campaignId}
          </p>
        </div>
        <Link to={`/campaigns/${campaignId}`} className="btn btn-secondary">
          ← Back to Campaign
        </Link>
      </div>

      <div className="card mb-6">
        <div className="flex gap-4">
          <button
            onClick={() => setShowHistory(false)}
            className={`btn ${!showHistory ? 'btn-primary' : 'btn-secondary'}`}
          >
            Latest Content
          </button>
          <button
            onClick={() => {
              setShowHistory(true)
              refetchHistory()
            }}
            className={`btn ${showHistory ? 'btn-primary' : 'btn-secondary'}`}
          >
            View History
          </button>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isLoading}
            className="btn btn-primary ml-auto"
          >
            {generateMutation.isLoading ? 'Generating...' : '+ Generate New Content'}
          </button>
        </div>
      </div>

      {showHistory ? (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Content History</h2>
          {history?.history?.length > 0 ? (
            <div className="space-y-6">
              {history.history.map((item, idx) => (
                <div key={item._id} className="border border-gray-200 rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="text-sm text-gray-500">
                        Generated: {new Date(item.generated_at).toLocaleString()}
                      </div>
                      {item.trends_used && (
                        <div className="text-sm text-gray-500 mt-1">
                          Trends: {item.trends_used.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="prose max-w-none">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-4 rounded">
                      {item.content}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No content history found. Generate some content first!
            </div>
          )}
        </div>
      ) : (
        <div className="card">
          {generateMutation.isLoading ? (
            <div className="text-center py-12">
              <div className="text-lg text-gray-600 mb-2">Generating content...</div>
              <div className="text-sm text-gray-500">This may take a minute</div>
            </div>
          ) : content?.content ? (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Generated Content</h2>
                {content.generated_at && (
                  <div className="text-sm text-gray-500">
                    {new Date(content.generated_at).toLocaleString()}
                  </div>
                )}
              </div>
              {content.content.startsWith('Error:') ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                  {content.content}
                </div>
              ) : (
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 bg-gray-50 p-6 rounded-lg">
                    {content.content}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">No content generated yet</p>
              <button
                onClick={() => generateMutation.mutate()}
                disabled={generateMutation.isLoading}
                className="btn btn-primary"
              >
                {generateMutation.isLoading ? 'Generating...' : 'Generate Content'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
