import { useState, useEffect } from 'react';
import { fetchTrades, type Trade } from '@services/api';

export default function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'TSLA'>('all');

  useEffect(() => {
    loadTrades();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const loadTrades = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTrades(filter === 'all' ? undefined : 'TSLA');
      setTrades(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch trades');
      console.error('Error fetching trades:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'filled':
        return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'cancelled':
        return 'bg-dark-surfaceHover text-dark-textSecondary border border-dark-border';
      case 'rejected':
        return 'bg-red-500/20 text-red-400 border border-red-500/30';
      default:
        return 'bg-dark-surfaceHover text-dark-textSecondary border border-dark-border';
    }
  };

  const getSideColor = (side: string) => {
    return side.toLowerCase() === 'buy'
      ? 'text-green-400 font-semibold'
      : 'text-red-400 font-semibold';
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-dark-text">Trade History</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-full font-medium transition-all ${
                filter === 'all'
                  ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                  : 'bg-dark-surfaceHover text-dark-textSecondary hover:bg-dark-border'
              }`}
            >
              All Trades
            </button>
            <button
              onClick={() => setFilter('TSLA')}
              className={`px-4 py-2 rounded-full font-medium transition-all ${
                filter === 'TSLA'
                  ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                  : 'bg-dark-surfaceHover text-dark-textSecondary hover:bg-dark-border'
              }`}
            >
              TSLA Only
            </button>
            <button
              onClick={loadTrades}
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
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl mb-4">
            {error}
          </div>
        )}

        {loading && trades.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            <p className="mt-2 text-dark-textSecondary">Loading trades...</p>
          </div>
        ) : trades.length === 0 ? (
          <p className="text-dark-textSecondary text-center py-12">No trades found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-dark-border">
              <thead className="bg-dark-surfaceHover">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Side
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Sentiment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-textSecondary uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-dark-surface divide-y divide-dark-border">
                {trades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-dark-surfaceHover transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-dark-text">
                      {trade.symbol}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${getSideColor(trade.side)}`}>
                      {trade.side.toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-textSecondary">
                      {trade.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-textSecondary">
                      ${trade.price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                          trade.status
                        )}`}
                      >
                        {trade.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-textSecondary">
                      {trade.sentiment_score !== null
                        ? trade.sentiment_score.toFixed(4)
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-textSecondary">
                      {new Date(trade.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
