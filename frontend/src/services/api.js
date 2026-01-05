import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 900000, // 15 minutes
  headers: {
    'Content-Type': 'application/json',
  },
})

// Campaigns API
export const campaignsAPI = {
  list: (status = null, limit = 50) =>
    api.get('/campaigns/list', { params: { status, limit } }),

  get: (campaignId) =>
    api.get(`/campaigns/${campaignId}`),

  create: (data) =>
    api.post('/campaigns/create', data),

  updateStatus: (campaignId, status) =>
    api.patch(`/campaigns/${campaignId}/status`, null, { params: { status } }),

  getStats: (campaignId) =>
    api.get(`/campaigns/${campaignId}/stats`),

  getRecommendations: (campaignId) =>
    api.get(`/campaigns/recommend/${campaignId}`),

  rerank: (campaignId) =>
    api.post(`/campaigns/${campaignId}/rerank`),
}

// Influencers API
export const influencersAPI = {
  search: (filters) => {
    // Filter out null, undefined, or empty string values
    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v != null && v !== '')
    )
    return api.get('/influencers/search', { params: cleanFilters })
  },

  get: (influencerId) =>
    api.get(`/influencers/${influencerId}`),

  getByChannel: (channelId) =>
    api.get(`/influencers/channel/${channelId}`),

  findSimilar: (channelId, topK = 10) =>
    api.get(`/influencers/find_similar/${channelId}`, { params: { top_k: topK } }),

  getRoi: (influencerId) =>
    api.get(`/influencers/${influencerId}/roi`),
}

// Content API
export const contentAPI = {
  generate: (campaignId) =>
    api.get(`/content/generate/${campaignId}`),

  getHistory: (campaignId, limit = 10) =>
    api.get(`/content/history/${campaignId}`, { params: { limit } }),

  getLatest: (campaignId) =>
    api.get(`/content/latest/${campaignId}`),
}

// Health API
export const healthAPI = {
  check: () =>
    api.get('/health/'),

  detailed: () =>
    api.get('/health/detailed'),
}

export default api

