import { useState } from 'react';
import TweetList from '@components/TweetList';
import StockChart from '@components/StockChart';
import SentimentAnalysis from '@components/SentimentAnalysis';
import TradeExecution from '@components/TradeExecution';
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

export default function HomePage() {
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);

  const handleTweetsLoaded = (loadedTweets: Tweet[]) => {
    setTweets(loadedTweets);
    // Reset analysis when new tweets are loaded
    setAnalysisResults(null);
  };

  const handleAnalysisComplete = (results: AnalysisResults) => {
    setAnalysisResults(results);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <header className="text-center mb-8">
        <h1 className="text-4xl font-bold text-dark-text mb-2 bg-gradient-to-r from-primary-400 to-violet-500 bg-clip-text text-transparent">
          TradeX Dashboard
        </h1>
        <p className="text-dark-textSecondary">Twitter Sentiment-Based Trading Platform</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Tweet List */}
        <div>
          <TweetList onTweetsLoaded={handleTweetsLoaded} />
        </div>

        {/* Stock Chart */}
        <div>
          <StockChart />
        </div>
      </div>

      {/* Sentiment Analysis */}
      <div className="mb-6">
        <SentimentAnalysis tweets={tweets} onAnalysisComplete={handleAnalysisComplete} />
      </div>

      {/* Trade Execution */}
      <div>
        <TradeExecution tweets={tweets} analysisResults={analysisResults} />
      </div>
    </div>
  );
}

