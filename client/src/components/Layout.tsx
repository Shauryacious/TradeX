import { Outlet, Link, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-dark-bg">
      <nav className="sticky top-0 z-50 bg-dark-bg/80 backdrop-blur-xl border-b border-dark-border">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-violet-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <span className="text-white font-bold text-xl">T</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-dark-text">TradeX</h1>
                <p className="text-xs text-dark-textSecondary">Trading Platform</p>
              </div>
            </Link>
            <div className="flex items-center space-x-2">
              <Link
                to="/"
                className={`px-5 py-2.5 rounded-full font-medium transition-all duration-200 ${
                  isActive('/')
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                    : 'text-dark-textSecondary hover:bg-dark-surfaceHover hover:text-dark-text'
                }`}
              >
                Home
              </Link>
              <Link
                to="/trades"
                className={`px-5 py-2.5 rounded-full font-medium transition-all duration-200 ${
                  isActive('/trades')
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                    : 'text-dark-textSecondary hover:bg-dark-surfaceHover hover:text-dark-text'
                }`}
              >
                Trades
              </Link>
              <Link
                to="/positions"
                className={`px-5 py-2.5 rounded-full font-medium transition-all duration-200 ${
                  isActive('/positions')
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                    : 'text-dark-textSecondary hover:bg-dark-surfaceHover hover:text-dark-text'
                }`}
              >
                Positions
              </Link>
            </div>
          </div>
        </div>
      </nav>
      <main className="pb-8">
        <Outlet />
      </main>
    </div>
  );
}
