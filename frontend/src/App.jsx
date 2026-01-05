import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import CampaignDetail from './pages/CampaignDetail'
import CreateCampaign from './pages/CreateCampaign'
import Influencers from './pages/Influencers'
import InfluencerDetail from './pages/InfluencerDetail'
import Content from './pages/Content'

function App() {
  try {
    return (
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/campaigns/create" element={<CreateCampaign />} />
            <Route path="/campaigns/:id" element={<CampaignDetail />} />
            <Route path="/influencers" element={<Influencers />} />
            <Route path="/influencers/:id" element={<InfluencerDetail />} />
            <Route path="/content/:campaignId" element={<Content />} />
          </Routes>
        </Layout>
      </Router>
    )
  } catch (error) {
    console.error('App error:', error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">App Error</h1>
          <p className="text-gray-600">{error.message}</p>
          <pre className="mt-4 text-left bg-gray-100 p-4 rounded text-sm overflow-auto max-w-2xl">
            {error.stack}
          </pre>
        </div>
      </div>
    )
  }
}

export default App
