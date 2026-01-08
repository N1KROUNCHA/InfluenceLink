import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 900000, // 15 minutes
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add Auth Token Interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  console.log("Request Interceptor running. URL:", config.url)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log("Attached Token:", token.substring(0, 10) + "...")
  } else {
    console.warn("No token found in localStorage!")
  }
  return config
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

// Auth API
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  onboard: (data) => api.post('/auth/influencer/onboard', data),
  profile: () => api.get('/auth/profile'),
  updateInfluencerProfile: (data) => api.put('/auth/influencer/profile', data)
}

// Content API
export const contentAPI = {
  generate: (campaignId) =>
    api.get(`/content/generate/${campaignId}`),

  getHistory: (campaignId, limit = 10) =>
    api.get(`/content/history/${campaignId}`, { params: { limit } }),

  getLatest: (campaignId) =>
    api.get(`/content/latest/${campaignId}`),

  generateCreatorStudio: (influencerId, prompt = null) =>
    api.get(`/content/creator-studio/${influencerId}`, { params: { prompt } }),

  saveCreatorContent: (data) =>
    api.post('/content/creator-studio/save', data),

  getCreatorHistory: (influencerId, campaignId = null) =>
    api.get(`/content/creator-studio/history/${influencerId}`, { params: { campaign_id: campaignId } }),
}

// Health API
export const healthAPI = {
  check: () =>
    api.get('/health/'),

  detailed: () =>
    api.get('/health/detailed'),
}

// Workflow API (CRM)
export const workflowAPI = {
  get: (campaignId) =>
    api.get(`/workflow/${campaignId}`),

  add: (campaignId, influencerId) =>
    api.post(`/workflow/${campaignId}/add/${influencerId}`),

  update: (campaignId, influencerId, data) =>
    api.put(`/workflow/${campaignId}/update/${influencerId}`, data),

  remove: (campaignId, influencerId) =>
    api.delete(`/workflow/${campaignId}/remove/${influencerId}`),

  getInfluencerWorkflow: (influencerId) =>
    api.get(`/workflow/my-collaborations/${influencerId}`),
}

export default api
