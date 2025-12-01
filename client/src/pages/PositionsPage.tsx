import { useState, useEffect } from 'react';
import { fetchPositions, type Position } from '@services/api';

export default function PositionsPage() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPositions();
  }, []);

  const loadPositions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPositions();
      setPositions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch positions');
      console.error('Error fetching positions:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
  const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-dark-text">Current Positions</h2>
          <button
            onClick={loadPositions}
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Loading...
              </span>
            ) : (
              'Refresh'
            )}
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl mb-4">
            {error}
          </div>
        )}

        {loading && positions.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            <p className="mt-2 text-dark-textSecondary">Loading positions...</p>
          </div>
        ) : positions.length === 0 ? (
          <p className="text-dark-textSecondary text-center py-12">No open positions</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {positions.map((position) => {
              const pnlPercent =
                position.average_price !== 0
                  ? ((position.unrealized_pnl / (position.average_price * position.quantity)) * 100)
                  : 0;

              return (
                <div
                  key={position.id}
                  className="border border-dark-border rounded-2xl p-6 hover:border-primary-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-primary-500/10 bg-dark-surfaceHover"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-dark-text">{position.symbol}</h3>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        position.unrealized_pnl >= 0
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}
                    >
                      {formatPercent(pnlPercent)}
                    </span>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-dark-textSecondary">Quantity:</span>
                      <span className="font-semibold text-dark-text">{position.quantity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-dark-textSecondary">Avg Price:</span>
                      <span className="font-semibold text-dark-text">
                        {formatCurrency(position.average_price)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-dark-textSecondary">Current Price:</span>
                      <span className="font-semibold text-primary-400">
                        {formatCurrency(position.current_price)}
                      </span>
                    </div>
                    <div className="border-t border-dark-border pt-3">
                      <div className="flex justify-between">
                        <span className="text-dark-textSecondary">Unrealized P&L:</span>
                        <span
                          className={`font-bold ${
                            position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                        >
                          {formatCurrency(position.unrealized_pnl)}
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-dark-textSecondary mt-2">
                      Updated: {new Date(position.updated_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
