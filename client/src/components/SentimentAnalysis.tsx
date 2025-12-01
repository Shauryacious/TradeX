import { useState } from 'react';
import type { Tweet } from '@services/api';

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

interface SentimentAnalysisProps {
  tweets: Tweet[];
  onAnalysisComplete?: (results: AnalysisResults) => void;
}

export default function SentimentAnalysis({ tweets, onAnalysisComplete }: SentimentAnalysisProps) {
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);

  const handleAnalyzeSentiment = () => {
    if (tweets.length === 0) {
      alert('Please fetch tweets first');
      return;
    }

    // Analyze sentiment from fetched tweets
    const analyzedTweets = tweets.filter((tweet) => tweet.sentiment_score !== null);
    
    if (analyzedTweets.length === 0) {
      alert('No tweets with sentiment analysis found');
      return;
    }

    const sentimentCounts = {
      positive: 0,
      negative: 0,
      neutral: 0,
    };

    let totalScore = 0;
    const sentimentBreakdown: { [key: string]: number[] } = {
      elonmusk: [],
      Tesla: [],
    };

    analyzedTweets.forEach((tweet) => {
      const label = tweet.sentiment_label?.toLowerCase() || 'neutral';
      if (label in sentimentCounts) {
        sentimentCounts[label as keyof typeof sentimentCounts]++;
      }
      if (tweet.sentiment_score !== null) {
        totalScore += tweet.sentiment_score;
        if (tweet.author_username in sentimentBreakdown) {
          sentimentBreakdown[tweet.author_username].push(tweet.sentiment_score);
        }
      }
    });

    const averageScore = totalScore / analyzedTweets.length;
    const overallSentiment =
      averageScore > 0.3 ? 'positive' : averageScore < -0.3 ? 'negative' : 'neutral';

    // Calculate average sentiment by author
    const authorAverages: { [key: string]: number } = {};
    Object.keys(sentimentBreakdown).forEach((author) => {
      const scores = sentimentBreakdown[author];
      if (scores.length > 0) {
        authorAverages[author] = scores.reduce((a, b) => a + b, 0) / scores.length;
      }
    });

    const results = {
      totalTweets: analyzedTweets.length,
      sentimentCounts,
      averageScore,
      overallSentiment,
      authorAverages,
      analyzedTweets,
    };
    
    setAnalysisResults(results);
    onAnalysisComplete?.(results);
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'text-green-400 bg-green-500/20 border border-green-500/30';
      case 'negative':
        return 'text-red-400 bg-red-500/20 border border-red-500/30';
      default:
        return 'text-dark-textSecondary bg-dark-surfaceHover border border-dark-border';
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-dark-text">Sentiment Analysis</h2>
        <button
          onClick={handleAnalyzeSentiment}
          disabled={tweets.length === 0}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          Run Analysis
        </button>
      </div>

      {tweets.length === 0 && (
        <div className="text-center py-8">
          <p className="text-dark-textSecondary">Please fetch tweets first to run sentiment analysis</p>
        </div>
      )}

      {analysisResults && (
        <div className="space-y-6">
          {/* Overall Results */}
          <div className="bg-gradient-to-br from-primary-500/10 to-violet-600/10 border border-primary-500/30 p-6 rounded-2xl">
            <h3 className="text-xl font-semibold text-dark-text mb-4">Overall Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center bg-dark-surfaceHover border border-dark-border rounded-xl p-4">
                <div className="text-3xl font-bold text-primary-400">
                  {analysisResults.totalTweets}
                </div>
                <div className="text-sm text-dark-textSecondary mt-1">Total Tweets Analyzed</div>
              </div>
              <div className="text-center bg-dark-surfaceHover border border-dark-border rounded-xl p-4">
                <div className="text-3xl font-bold text-violet-400">
                  {analysisResults.averageScore.toFixed(4)}
                </div>
                <div className="text-sm text-dark-textSecondary mt-1">Average Sentiment Score</div>
              </div>
              <div className="text-center bg-dark-surfaceHover border border-dark-border rounded-xl p-4">
                <div
                  className={`text-2xl font-bold px-4 py-2 rounded-xl inline-block ${getSentimentColor(
                    analysisResults.overallSentiment
                  )}`}
                >
                  {analysisResults.overallSentiment.toUpperCase()}
                </div>
                <div className="text-sm text-dark-textSecondary mt-2">Overall Sentiment</div>
              </div>
            </div>
          </div>

          {/* Sentiment Distribution */}
          <div>
            <h3 className="text-lg font-semibold text-dark-text mb-3">Sentiment Distribution</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-green-500/10 border border-green-500/30 p-4 rounded-xl text-center">
                <div className="text-2xl font-bold text-green-400">
                  {analysisResults.sentimentCounts.positive}
                </div>
                <div className="text-sm text-green-400/80 mt-1">Positive</div>
              </div>
              <div className="bg-dark-surfaceHover border border-dark-border p-4 rounded-xl text-center">
                <div className="text-2xl font-bold text-dark-textSecondary">
                  {analysisResults.sentimentCounts.neutral}
                </div>
                <div className="text-sm text-dark-textSecondary mt-1">Neutral</div>
              </div>
              <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-xl text-center">
                <div className="text-2xl font-bold text-red-400">
                  {analysisResults.sentimentCounts.negative}
                </div>
                <div className="text-sm text-red-400/80 mt-1">Negative</div>
              </div>
            </div>
          </div>

          {/* Author Breakdown */}
          {Object.keys(analysisResults.authorAverages).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-dark-text mb-3">Sentiment by Author</h3>
              <div className="space-y-2">
                {Object.entries(analysisResults.authorAverages).map(([author, score]) => (
                  <div key={author} className="flex items-center justify-between bg-dark-surfaceHover border border-dark-border p-4 rounded-xl">
                    <span className="font-semibold text-dark-text">@{author}</span>
                    <div className="flex items-center gap-4">
                      <span className="text-dark-textSecondary">Score: <span className="text-primary-400 font-semibold">{score.toFixed(4)}</span></span>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${getSentimentColor(
                          score > 0.3 ? 'positive' : score < -0.3 ? 'negative' : 'neutral'
                        )}`}
                      >
                        {score > 0.3 ? 'Positive' : score < -0.3 ? 'Negative' : 'Neutral'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Tweet Analysis */}
          <div>
            <h3 className="text-lg font-semibold text-dark-text mb-3">Tweet Details</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {analysisResults.analyzedTweets.map((tweet) => (
                <div
                  key={tweet.id}
                  className="border border-dark-border rounded-xl p-3 text-sm bg-dark-surfaceHover"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-dark-text">@{tweet.author_username}</span>
                    <span
                      className={`px-2 py-1 rounded-lg text-xs ${getSentimentColor(
                        tweet.sentiment_label || 'neutral'
                      )}`}
                    >
                      {tweet.sentiment_label} ({tweet.sentiment_score?.toFixed(4)})
                    </span>
                  </div>
                  <p className="text-dark-textSecondary line-clamp-2">{tweet.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
