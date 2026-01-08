import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const location = useLocation()

  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isBrand = user.type === 'brand'

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-primary-600">InfluenceLink</h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {isBrand ? (
                  <>
                    <Link
                      to="/"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/') && location.pathname === '/'
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      Dashboard
                    </Link>
                    <Link
                      to="/campaigns"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/campaigns')
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      Campaigns
                    </Link>
                    <Link
                      to="/influencers"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/influencers')
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      Influencers
                    </Link>
                    <Link
                      to="/profile"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/profile')
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      Brand Profile
                    </Link>
                  </>
                ) : (
                  <>
                    <Link
                      to="/"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/') && location.pathname === '/'
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      My Dashboard
                    </Link>
                    <Link
                      to="/collaborations"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/collaborations')
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      Collaboration Hub
                    </Link>
                    <Link
                      to="/studio"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/studio')
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      AI Content Studio
                    </Link>
                    <Link
                      to="/profile"
                      className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive('/profile')
                        ? 'border-primary-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                      My Profile
                    </Link>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={() => {
                  if (confirm("Sign out of InfluenceLink?")) {
                    localStorage.removeItem('token')
                    localStorage.removeItem('user')
                    window.location.href = '/login'
                  }
                }}
                className="ml-4 px-4 py-2 text-xs font-black uppercase tracking-widest text-gray-500 hover:text-red-600 transition-colors border border-gray-200 rounded-lg hover:border-red-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}
