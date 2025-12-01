import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { fetchStockData, fetchStockHistory } from '@services/api';
import type { StockData, ChartDataPoint } from '@services/api';

export default function StockChart() {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetchStockData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch current data first, then history with a small delay to avoid rate limiting
      const currentData = await fetchStockData('TSLA');
      setStockData(currentData);
      
      // Small delay to avoid hitting rate limits
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const historyData = await fetchStockHistory('TSLA', 30);
      setChartData(historyData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch stock data';
      setError(errorMessage);
      console.error('Error fetching stock data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
  const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ value: number; payload: { date: string } }> }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-surface border border-dark-border rounded-xl p-3 shadow-xl">
          <p className="text-dark-textSecondary text-sm">{payload[0].payload.date}</p>
          <p className="text-primary-400 font-semibold">{formatCurrency(payload[0].value)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-dark-text">Tesla Stock Data</h2>
        <button
          onClick={handleFetchStockData}
          disabled={loading}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Fetching...
            </span>
          ) : (
            'Fetch Stock Data'
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl mb-4">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
              {error.includes('Rate limit') && (
                <p className="text-xs mt-2 text-red-300">
                  The API is temporarily rate-limited. The system will automatically retry, or you can try again in a few moments.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {stockData?.stale && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 px-4 py-3 rounded-xl mb-4">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold">Cached Data</p>
              <p className="text-sm">{stockData.message || 'Showing cached data due to rate limiting. Data may not be up-to-date.'}</p>
            </div>
          </div>
        </div>
      )}

      {stockData && (
        <div className="mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-dark-surfaceHover border border-dark-border p-4 rounded-xl">
              <div className="text-sm text-dark-textSecondary mb-1">Current Price</div>
              <div className="text-2xl font-bold text-dark-text">
                {formatCurrency(stockData.price)}
              </div>
            </div>
            <div className="bg-dark-surfaceHover border border-dark-border p-4 rounded-xl">
              <div className="text-sm text-dark-textSecondary mb-1">Change</div>
              <div
                className={`text-2xl font-bold ${
                  stockData.change >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {formatCurrency(stockData.change)} ({formatPercent(stockData.changePercent)})
              </div>
            </div>
            <div className="bg-dark-surfaceHover border border-dark-border p-4 rounded-xl">
              <div className="text-sm text-dark-textSecondary mb-1">Volume</div>
              <div className="text-2xl font-bold text-dark-text">
                {(stockData.volume / 1000000).toFixed(2)}M
              </div>
            </div>
            <div className="bg-dark-surfaceHover border border-dark-border p-4 rounded-xl">
              <div className="text-sm text-dark-textSecondary mb-1">High / Low</div>
              <div className="text-lg font-semibold text-dark-text">
                {formatCurrency(stockData.high)} / {formatCurrency(stockData.low)}
              </div>
            </div>
          </div>
        </div>
      )}

      {chartData.length > 0 && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold text-dark-text mb-4">30-Day Price Chart</h3>
          <div className="bg-dark-surfaceHover border border-dark-border rounded-xl p-4">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2F3336" />
                <XAxis 
                  dataKey="date" 
                  stroke="#71767A"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#71767A"
                  style={{ fontSize: '12px' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  wrapperStyle={{ color: '#E7E9EA' }}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#8B5CF6"
                  strokeWidth={3}
                  name="Price"
                  dot={false}
                  activeDot={{ r: 6, fill: '#8B5CF6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {!stockData && !loading && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-dark-surfaceHover flex items-center justify-center">
            <svg className="w-8 h-8 text-dark-textSecondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-dark-textSecondary">Click "Fetch Stock Data" to load Tesla stock information and chart</p>
        </div>
      )}
    </div>
  );
}
