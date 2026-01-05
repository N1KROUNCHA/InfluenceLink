import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { campaignsAPI } from '../services/api'

export default function CreateCampaign() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    brand_id: 1,
    campaign_name: '',
    category: '',
    budget: '',
    min_subscribers: '',
    max_subscribers: '',
    target_region: '',
    target_language: '',
    required_style: '',
    authenticity_threshold: 0.7,
    dna_similarity_threshold: 0.8,
  })

  const mutation = useMutation({
    mutationFn: (data) => campaignsAPI.create(data),
    onSuccess: (response) => {
      alert('Campaign created successfully!')
      navigate(`/campaigns/${response.data.campaign_id}`)
    },
    onError: (error) => {
      alert('Error creating campaign: ' + (error.response?.data?.detail || error.message))
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Create New Campaign</h1>
      
      <form onSubmit={handleSubmit} className="card space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="label">Campaign Name *</label>
            <input
              type="text"
              name="campaign_name"
              value={formData.campaign_name}
              onChange={handleChange}
              className="input"
              required
            />
          </div>
          
          <div>
            <label className="label">Category *</label>
            <input
              type="text"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="input"
              placeholder="e.g., Tech, Beauty, Education"
              required
            />
          </div>
          
          <div>
            <label className="label">Budget</label>
            <input
              type="number"
              name="budget"
              value={formData.budget}
              onChange={handleChange}
              className="input"
              placeholder="0.00"
            />
          </div>
          
          <div>
            <label className="label">Target Region *</label>
            <input
              type="text"
              name="target_region"
              value={formData.target_region}
              onChange={handleChange}
              className="input"
              placeholder="e.g., US, Global"
              required
            />
          </div>
          
          <div>
            <label className="label">Target Language</label>
            <input
              type="text"
              name="target_language"
              value={formData.target_language}
              onChange={handleChange}
              className="input"
              placeholder="e.g., English"
            />
          </div>
          
          <div>
            <label className="label">Required Style</label>
            <input
              type="text"
              name="required_style"
              value={formData.required_style}
              onChange={handleChange}
              className="input"
              placeholder="e.g., Professional, Casual"
            />
          </div>
          
          <div>
            <label className="label">Min Subscribers</label>
            <input
              type="number"
              name="min_subscribers"
              value={formData.min_subscribers}
              onChange={handleChange}
              className="input"
            />
          </div>
          
          <div>
            <label className="label">Max Subscribers</label>
            <input
              type="number"
              name="max_subscribers"
              value={formData.max_subscribers}
              onChange={handleChange}
              className="input"
            />
          </div>
          
          <div>
            <label className="label">Authenticity Threshold</label>
            <input
              type="number"
              name="authenticity_threshold"
              value={formData.authenticity_threshold}
              onChange={handleChange}
              className="input"
              step="0.1"
              min="0"
              max="1"
            />
          </div>
          
          <div>
            <label className="label">DNA Similarity Threshold</label>
            <input
              type="number"
              name="dna_similarity_threshold"
              value={formData.dna_similarity_threshold}
              onChange={handleChange}
              className="input"
              step="0.1"
              min="0"
              max="1"
            />
          </div>
        </div>
        
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={mutation.isLoading}
            className="btn btn-primary flex-1"
          >
            {mutation.isLoading ? 'Creating...' : 'Create Campaign'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/campaigns')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

