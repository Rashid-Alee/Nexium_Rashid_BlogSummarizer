'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
// Import our API utility
import { api } from '@/lib/api';

export default function BlogSummarizer() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showUrdu, setShowUrdu] = useState(false);
  
  // Notification system
  const [notification, setNotification] = useState(null);

  // API connection status
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API health on component mount
  useEffect(() => {
    checkApiConnection();
  }, []);

  const checkApiConnection = async () => {
    try {
      console.log(`🔍 Checking API connection to: ${api.getApiUrl()}`);
      const health = await api.checkHealth();
      setApiStatus('connected');
      console.log('✅ API connected successfully:', health);
    } catch (error) {
      setApiStatus('disconnected');
      console.error('❌ API connection failed:', error);
    }
  };

  //Auto-hide notification after 10 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Show notification function
  const showNotification = (type, message, details = null) => {
    setNotification({ type, message, details });
  };

  const calculateReadingTime = (wordCount) => {
    if (!wordCount) return 0;
    return Math.ceil(wordCount / 200);
  };

  const handleScrape = async () => {
    if (!url) {
      setError('Please enter a valid URL');
      return;
    }

    setError('');
    setResult(null);
    setLoading(true);
    setNotification(null);

    try {
      console.log(`🚀 Starting blog scrape for: ${url}`);
      
      // Use our API utility instead of hardcoded localhost
      const data = await api.scrapeBlog(url);

      if (data.success) {
        setResult(data.data);
        
        //Show appropriate notification based on cache status
        if (data.cached) {
          showNotification('info', 'Retrieved from cache', {
            message: 'This article was previously analyzed',
            responseTime: data.performance?.response_time_ms || 'Unknown'
          });
        } else {
          // Check database save status
          const dbStatus = data.database;
          if (dbStatus?.overall_success) {
            showNotification('success', 'Article analyzed & saved successfully!', {
              supabase: dbStatus.supabase?.success ? 'Summary saved' : 'Summary failed',
              mongodb: dbStatus.mongodb?.success ? 'Content saved' : 'Content failed',
              totalTime: data.performance?.total_time_ms || 'Unknown'
            });
          } else {
            showNotification('warning', 'Analysis completed with partial save', {
              supabase: dbStatus?.supabase?.success ? 'Summary saved' : 'Summary failed',
              mongodb: dbStatus?.mongodb?.success ? 'Content saved' : 'Content failed'
            });
          }
        }
      } else {
        setError(data.error || 'Failed to analyze the article');
      }
    } catch (err) {
      console.error('❌ Scraping error:', err);
      setError('Unable to connect to the API. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      
      {/* API Status Indicator */}
      <div className="fixed top-4 right-4 z-50">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          apiStatus === 'connected' 
            ? 'bg-green-100 text-green-800' 
            : apiStatus === 'disconnected'
            ? 'bg-red-100 text-red-800'
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          API: {apiStatus === 'connected' ? '🟢 Connected' : apiStatus === 'disconnected' ? '🔴 Disconnected' : '🟡 Checking...'}
        </div>
      </div>

      {/* Floating Notification */}
      {notification && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md w-full mx-4">
          <Alert className={`shadow-lg border-l-4 ${
            notification.type === 'success' 
              ? 'border-l-green-500 bg-green-50' 
              : notification.type === 'warning'
              ? 'border-l-yellow-500 bg-yellow-50'
              : 'border-l-blue-500 bg-blue-50'
          }`}>
            <AlertDescription className="text-sm">
              <div className="font-medium mb-1">{notification.message}</div>
              {notification.details && (
                <div className="text-xs text-gray-600 space-y-1">
                  {typeof notification.details === 'object' ? (
                    Object.entries(notification.details).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace(/([A-Z])/g, ' $1')}:</span>
                        <span className="font-mono">{value}</span>
                      </div>
                    ))
                  ) : (
                    <div>{notification.details}</div>
                  )}
                </div>
              )}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Header */}
      <header className="text-center py-16">
        <div className="max-w-3xl mx-auto px-6">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI Blog Summarizer
          </h1>
          <p className="text-xl text-gray-600 leading-relaxed">
            Transform any blog post into concise, intelligent summaries. 
            Available in English and Urdu.
          </p>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-12">
        
        {/* Clean Input Section */}
        <div className="mb-12">
          <Card className="shadow-lg border-0 bg-white/90 backdrop-blur-sm">
            <CardContent className="p-8">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Article URL
                  </label>
                  <div className="flex gap-3">
                    <Input
                      type="url"
                      placeholder="https://example.com/article"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      className="flex-1 h-12 text-base"
                      onKeyPress={(e) => e.key === 'Enter' && handleScrape()}
                    />
                    <Button 
                      onClick={handleScrape}
                      disabled={loading || !url.trim() || apiStatus !== 'connected'}
                      className="h-12 px-8 bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? (
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          Analyzing...
                        </div>
                      ) : (
                        'Analyze'
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Error Display */}
        {error && (
          <Alert className="mb-6 border-l-4 border-l-red-500 bg-red-50">
            <AlertDescription className="text-red-700">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-6">
            
            {/* Summary Controls */}
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <Button
                variant="outline"
                onClick={() => setShowUrdu(!showUrdu)}
                className="bg-white/80"
              >
                {showUrdu ? 'Show English' : 'Show Urdu'}
              </Button>
            </div>

            {/* Article Info */}
            <Card className="bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-lg">{result.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="font-semibold text-blue-700">{result.word_count}</div>
                    <div className="text-gray-600">Words</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="font-semibold text-green-700">{calculateReadingTime(result.word_count)} min</div>
                    <div className="text-gray-600">Read Time</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="font-semibold text-purple-700">{result.paragraph_count}</div>
                    <div className="text-gray-600">Paragraphs</div>
                  </div>
                  <div className="text-center p-3 bg-yellow-50 rounded-lg">
                    <div className="font-semibold text-yellow-700">{result.char_count}</div>
                    <div className="text-gray-600">Characters</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Summary */}
            <Card className="bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  🤖 AI Summary {showUrdu && '(اردو میں)'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 leading-relaxed text-lg">
                  {showUrdu ? result.ai_summary_urdu : result.ai_summary}
                </p>
                
                {/* Summary Stats */}
                {result.summary_stats && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>Compression: {result.summary_stats.compression_ratio}</div>
                      <div>Important terms found: {result.summary_stats.important_words_found}</div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Translation Stats */}
            {result.translation_stats && showUrdu && (
              <Card className="bg-white/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-sm">Translation Details</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-gray-600">
                  <div className="grid grid-cols-2 gap-2">
                    <div>Method: {result.translation_stats.method}</div>
                    <div>Confidence: {result.translation_stats.confidence}</div>
                    <div>Coverage: {result.translation_stats.coverage}%</div>
                    <div>Words translated: {result.translation_stats.words_translated}/{result.translation_stats.total_words}</div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Footer */}
        <footer className="text-center py-12 text-gray-500 text-sm">
          <p>AI-powered blog analysis with dual-language support</p>
          <p className="mt-2">Backend API: {api.getApiUrl()}</p>
        </footer>
      </main>
    </div>
  );
}