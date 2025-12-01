import { useState } from 'react';
import { executeTrade } from '@services/api';
import type { Trade, TradeRequest, Tweet } from '@services/api';

interface AnalysisResults {
  totalTweets: number;
  sentimentCounts: {
    positive: number;
    negative: number;
    neutral: number;
  };
  averageScore: number;
  overallSentiment: string;
  authorAverages: { [key: string]: number };
  analyzedTweets: Tweet[];
}

interface TradeExecutionProps {
  tweets: Tweet[];
  analysisResults: AnalysisResults | null;
}

export default function TradeExecution({ analysisResults }: TradeExecutionProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [lastTrade, setLastTrade] = useState<Trade | null>(null);

  const handleExecuteTrade = async () => {
    if (!analysisResults) {
      alert('Please run sentiment analysis first');
      return;
    }

    if (analysisResults.overallSentiment === 'neutral') {
      alert('Overall sentiment is neutral. No trade will be executed.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Use the average sentiment score for trade execution
      const sentimentScore = analysisResults.averageScore;
      
      // Determine trade side based on sentiment
      const tradeRequest: TradeRequest = {
        symbol: 'TSLA',
        sentiment_score: sentimentScore,
        reason: `Sentiment-based trade: ${analysisResults.overallSentiment} sentiment (${sentimentScore.toFixed(4)})`,
      };

      const trade = await executeTrade(tradeRequest);
      setLastTrade(trade);
      setSuccess(`Trade executed successfully! Order ID: ${trade.order_id || 'N/A'}`);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage =
        error.response?.data?.detail || error.message || 'Failed to execute trade';
      setError(errorMessage);
      console.error('Error executing trade:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTradeRecommendation = () => {
    if (!analysisResults) return null;

    const { overallSentiment, averageScore } = analysisResults;
    
    if (overallSentiment === 'positive' && averageScore > 0.3) {
      return {
        action: 'BUY',
        color: 'text-green-400',
        bgColor: 'bg-green-500/20',
        borderColor: 'border-green-500/30',
        message: `Strong positive sentiment detected. Recommended action: BUY`,
      };
    } else if (overallSentiment === 'negative' && averageScore < -0.3) {
      return {
        action: 'SELL',
        color: 'text-red-400',
        bgColor: 'bg-red-500/20',
        borderColor: 'border-red-500/30',
        message: `Negative sentiment detected. Recommended action: SELL`,
      };
    } else {
      return {
        action: 'HOLD',
        color: 'text-dark-textSecondary',
        bgColor: 'bg-dark-surfaceHover',
        borderColor: 'border-dark-border',
        message: `Neutral sentiment. Recommended action: HOLD`,
      };
    }
  };

  const recommendation = getTradeRecommendation();

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-dark-text">Execute Trade</h2>
        <button
          onClick={handleExecuteTrade}
          disabled={loading || !analysisResults || recommendation?.action === 'HOLD'}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Executing...
            </span>
          ) : (
            'Execute Trade'
          )}
        </button>
      </div>

      {!analysisResults && (
        <div className="text-center py-8">
          <p className="text-dark-textSecondary">Please run sentiment analysis first to execute a trade</p>
        </div>
      )}

      {recommendation && analysisResults && (
        <div className={`${recommendation.bgColor} border ${recommendation.borderColor} p-6 rounded-2xl mb-4`}>
          <div className="flex items-center justify-between">
            <div>
              <div className={`text-lg font-semibold ${recommendation.color} mb-1`}>
                {recommendation.message}
              </div>
              <div className="text-sm text-dark-textSecondary">
                Average Sentiment Score: <span className="text-primary-400 font-semibold">{analysisResults.averageScore.toFixed(4)}</span>
              </div>
            </div>
            <div
              className={`text-3xl font-bold px-6 py-3 rounded-xl ${recommendation.color} ${recommendation.bgColor} border-2 ${recommendation.borderColor}`}
            >
              {recommendation.action}
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-500/10 border border-green-500/30 text-green-400 px-4 py-3 rounded-xl mb-4">
          {success}
        </div>
      )}

      {lastTrade && (
        <div className="bg-dark-surfaceHover border border-dark-border rounded-xl p-5 mt-4">
          <h3 className="font-semibold text-dark-text mb-3">Last Trade Details</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-dark-textSecondary">Symbol:</span>
              <span className="font-semibold ml-2 text-dark-text">{lastTrade.symbol}</span>
            </div>
            <div>
              <span className="text-dark-textSecondary">Side:</span>
              <span className={`font-semibold ml-2 uppercase ${
                lastTrade.side.toLowerCase() === 'buy' ? 'text-green-400' : 'text-red-400'
              }`}>
                {lastTrade.side}
              </span>
            </div>
            <div>
              <span className="text-dark-textSecondary">Quantity:</span>
              <span className="font-semibold ml-2 text-dark-text">{lastTrade.quantity}</span>
            </div>
            <div>
              <span className="text-dark-textSecondary">Price:</span>
              <span className="font-semibold ml-2 text-primary-400">${lastTrade.price.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-dark-textSecondary">Status:</span>
              <span className="font-semibold ml-2 text-dark-text">{lastTrade.status}</span>
            </div>
            <div>
              <span className="text-dark-textSecondary">Order ID:</span>
              <span className="font-semibold ml-2 text-dark-text">{lastTrade.order_id || 'N/A'}</span>
            </div>
            {lastTrade.reason && (
              <div className="col-span-2">
                <span className="text-dark-textSecondary">Reason:</span>
                <span className="ml-2 text-dark-text">{lastTrade.reason}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
