import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import CampaignDetail from './pages/CampaignDetail'
import CreateCampaign from './pages/CreateCampaign'
import Influencers from './pages/Influencers'
import InfluencerDetail from './pages/InfluencerDetail'
import Content from './pages/Content'
import Login from './pages/Login'
import Register from './pages/Register'
import InfluencerOnboarding from './pages/InfluencerOnboarding'
import BrandProfile from './pages/BrandProfile'
import InfluencerDashboard from './pages/InfluencerDashboard'
import CollaborationHub from './pages/CollaborationHub'
import InfluencerProfileEdit from './pages/InfluencerProfileEdit'
import InfluencerContentStudio from './pages/InfluencerContentStudio'

function PrivateRoutes() {
  const token = localStorage.getItem('token')
  return token ? <Layout><Outlet /></Layout> : <Navigate to="/login" />
}

function App() {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isBrand = user.type === 'brand'

  try {
    return (
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Authenticated Routes */}
          <Route element={<PrivateRoutes />}>
            <Route path="/" element={isBrand ? <Dashboard /> : <InfluencerDashboard />} />
            <Route path="/dashboard" element={isBrand ? <Dashboard /> : <InfluencerDashboard />} />
            <Route path="/collaborations" element={<CollaborationHub />} />
            <Route path="/studio" element={<InfluencerContentStudio />} />
            <Route path="/onboard" element={<InfluencerOnboarding />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/campaigns/create" element={<CreateCampaign />} />
            <Route path="/campaigns/:id" element={<CampaignDetail />} />
            <Route path="/influencers" element={<Influencers />} />
            <Route path="/influencers/:id" element={<InfluencerDetail />} />
            <Route path="/content/:campaignId" element={<Content />} />
            <Route path="/profile" element={isBrand ? <BrandProfile /> : <InfluencerProfileEdit />} />
          </Route>

          {/* Catch all */}
          {/* <Route path="*" element={<Navigate to="/" />} /> */}
        </Routes>
      </Router>
    )
  } catch (error) {
    console.error('App error:', error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">App Error</h1>
          <p className="text-gray-600">{error.message}</p>
        </div>
      </div>
    )
  }
}

export default App
