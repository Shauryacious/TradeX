import { useState } from 'react';
import { fetchTweetsFromTwitter } from '@services/api';
import type { Tweet } from '@services/api';
import type { AxiosError } from 'axios';

interface TweetListProps {
  onTweetsLoaded?: (tweets: Tweet[]) => void;
}

export default function TweetList({ onTweetsLoaded }: TweetListProps) {
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessages, setStatusMessages] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [tweetCount, setTweetCount] = useState<number>(10);

  const handleFetchTweets = async () => {
    setLoading(true);
    setError(null);
    setStatusMessages([]);
    setCurrentStep('Initializing...');
    
    try {
      // Fetch tweets from Elon Musk's official account
      const usernames = ['elonmusk'];
      const allTweets: Tweet[] = [];
      const allStatusMessages: string[] = [];
      
      for (const username of usernames) {
        setCurrentStep(`Fetching tweets from @${username}...`);
        
        try {
          const response = await fetchTweetsFromTwitter(username, tweetCount);
          
          // Update status messages
          allStatusMessages.push(...response.status_messages);
          setStatusMessages([...allStatusMessages]);
          
          // Check if the request was successful
          if (!response.success) {
            // API returned success: false (e.g., rate limit or user not found)
            setCurrentStep(`⚠️ ${response.message}`);
            // Continue to next username instead of failing completely
            continue;
          }
          
          // Add fetched tweets
          allTweets.push(...response.tweets);
          
          // Update current step
          setCurrentStep(
            `Fetched ${response.tweets_fetched} tweet(s) from @${username} ` +
            `(${response.tweets_saved} new, ${response.tweets_skipped} existing)`
          );
        } catch (fetchError) {
          // Handle network/API errors
          const axiosError = fetchError as AxiosError<{ detail?: string; message?: string }>;
          const errorDetail = axiosError?.response?.data?.detail || 
                            axiosError?.response?.data?.message ||
                            axiosError?.message || 
                            'Failed to fetch tweets';
          
          allStatusMessages.push(`❌ Error fetching from @${username}: ${errorDetail}`);
          setStatusMessages([...allStatusMessages]);
          setCurrentStep(`⚠️ Error fetching from @${username}`);
          // Continue to next username instead of failing completely
        }
      }
      
      // Sort all tweets by date
      const sortedTweets = allTweets.sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      
      setTweets(sortedTweets);
      
      if (sortedTweets.length > 0) {
        setCurrentStep(`✅ Completed! Loaded ${sortedTweets.length} tweet(s)`);
        onTweetsLoaded?.(sortedTweets);
      } else {
        setCurrentStep(`⚠️ No tweets were fetched. Check the process log above for details.`);
      }
    } catch (err) {
      // Extract error message from axios error or generic error
      let errorMessage = 'Failed to fetch tweets';
      const axiosError = err as AxiosError<{ detail?: string; message?: string }>;
      
      if (axiosError?.response?.data?.detail) {
        errorMessage = axiosError.response.data.detail;
      } else if (axiosError?.response?.data?.message) {
        errorMessage = axiosError.response.data.message;
      } else if (axiosError?.message) {
        errorMessage = axiosError.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      // Check if it's a network error
      if (axiosError?.code === 'ERR_NETWORK' || axiosError?.message?.includes('Network Error')) {
        errorMessage = 'Cannot connect to server. Please make sure the backend server is running on http://localhost:8000';
      }
      
      setError(errorMessage);
      setCurrentStep(`❌ Error: ${errorMessage}`);
      console.error('Error fetching tweets:', err);
    } finally {
      setLoading(false);
      // Clear current step after a delay
      setTimeout(() => {
        setCurrentStep('');
      }, 3000);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-dark-text">Latest Tweets</h2>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label htmlFor="tweet-count" className="text-sm text-dark-textSecondary">
              Number of tweets:
            </label>
            <input
              id="tweet-count"
              type="number"
              min="1"
              max="100"
              value={tweetCount}
              onChange={(e) => setTweetCount(Math.max(1, Math.min(100, parseInt(e.target.value) || 10)))}
              disabled={loading}
              className="w-20 px-3 py-1.5 bg-dark-surface border border-dark-border rounded-lg text-dark-text text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
          <button
            onClick={handleFetchTweets}
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Fetching...
              </span>
            ) : (
              'Fetch Tweets'
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl mb-4">
          {error}
        </div>
      )}

      {currentStep && (
        <div className="bg-primary-500/10 border border-primary-500/30 text-primary-400 px-4 py-3 rounded-xl mb-4">
          <div className="flex items-center gap-2">
            {loading && (
              <span className="w-4 h-4 border-2 border-primary-400 border-t-transparent rounded-full animate-spin"></span>
            )}
            <span className="font-medium">{currentStep}</span>
          </div>
        </div>
      )}

      {statusMessages.length > 0 && (
        <div className="bg-dark-surfaceHover border border-dark-border rounded-xl p-4 mb-4 max-h-48 overflow-y-auto">
          <h3 className="text-sm font-semibold text-dark-text mb-2">Process Log:</h3>
          <div className="space-y-1">
            {statusMessages.map((msg, idx) => (
              <div key={idx} className="text-xs text-dark-textSecondary font-mono">
                <span className="text-primary-400">[{idx + 1}]</span> {msg}
              </div>
            ))}
          </div>
        </div>
      )}

      {tweets.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-dark-surfaceHover flex items-center justify-center">
            <svg className="w-8 h-8 text-dark-textSecondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <p className="text-dark-textSecondary">Click "Fetch Tweets" to load tweets from Elon Musk (@elonmusk)</p>
        </div>
      )}

      <div className="space-y-4">
        {tweets.map((tweet) => (
          <div
            key={tweet.id}
            className="bg-dark-surfaceHover border border-dark-border rounded-2xl p-5 hover:border-primary-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-primary-500/10"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-violet-600 flex items-center justify-center font-bold text-white">
                  {tweet.author_username.charAt(0).toUpperCase()}
                </div>
                <div>
                  <span className="font-semibold text-dark-text">@{tweet.author_username}</span>
                </div>
              </div>
              <span className="text-sm text-dark-textSecondary">
                {new Date(tweet.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-dark-text leading-relaxed">{tweet.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
