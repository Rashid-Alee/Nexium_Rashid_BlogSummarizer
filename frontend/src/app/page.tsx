'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function BlogSummarizer() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showUrdu, setShowUrdu] = useState(false);
  
  // Notification system
  const [notification, setNotification] = useState(null);

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
      const response = await fetch('http://localhost:8000/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });

      const data = await response.json();

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
      setError('Unable to connect. Make sure your backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      
      {/*Notification Component - Center Top Position */}
      {notification && (
        <div className="fixed top-8 left-1/2 transform -translate-x-1/2 z-[9999] w-full max-w-md px-4">
          <div className="animate-in slide-in-from-top-4 duration-500 ease-out">
            <Alert 
              className={`border-l-4 shadow-2xl border backdrop-blur-sm ${
                notification.type === 'success' 
                  ? 'border-l-green-500 bg-green-50/95 border-green-200' 
                  : notification.type === 'warning'
                  ? 'border-l-yellow-500 bg-yellow-50/95 border-yellow-200'
                  : 'border-l-blue-500 bg-blue-50/95 border-blue-200'
              }`}
            >
            <div className="flex items-start justify-between p-4">
              <div className="flex-1">
                <div className="flex items-center">
                  {notification.type === 'success' && (
                    <div className="flex-shrink-0 mr-3">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  {notification.type === 'warning' && (
                    <div className="flex-shrink-0 mr-3">
                      <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  {notification.type === 'info' && (
                    <div className="flex-shrink-0 mr-3">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                  
                  <div className="flex-1">
                    <div className={`font-semibold text-base ${
                      notification.type === 'success' ? 'text-green-800' :
                      notification.type === 'warning' ? 'text-yellow-800' : 'text-blue-800'
                    }`}>
                      {notification.message}
                    </div>
                
                    {notification.details && (
                      <div className="mt-2 text-sm text-gray-600">
                        {notification.details.message && (
                          <div className="mb-1">{notification.details.message}</div>
                        )}
                        {(notification.details.supabase || notification.details.mongodb) && (
                          <div className="flex flex-wrap gap-3 mt-2">
                            {notification.details.supabase && (
                              <span className="flex items-center text-xs">
                                <span className="w-2 h-2 bg-blue-500 rounded-full mr-1.5"></span>
                                Supabase: {notification.details.supabase}
                              </span>
                            )}
                            {notification.details.mongodb && (
                              <span className="flex items-center text-xs">
                                <span className="w-2 h-2 bg-green-500 rounded-full mr-1.5"></span>
                                MongoDB: {notification.details.mongodb}
                              </span>
                            )}
                          </div>
                        )}
                        {(notification.details.responseTime || notification.details.totalTime) && (
                          <div className="text-xs text-gray-500 mt-1">
                            ⚡ Response time: {notification.details.responseTime || notification.details.totalTime}ms
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => setNotification(null)}
                className="ml-4 text-gray-400 hover:text-gray-600 transition-colors duration-200 p-1 rounded-full hover:bg-gray-100"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </Alert>
        </div>
      </div>
    )}

      {/* Minimal Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-6 py-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Article Summarizer
          </h1>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Get instant AI summaries from any article. Available in English and Urdu.
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
                      disabled={loading || !url.trim()}
                      className="h-12 px-8 bg-blue-600 hover:bg-blue-700"
                    >
                      {loading ? "Analyzing..." : "Summarize"}
                    </Button>
                  </div>
                </div>
                
                {error && (
                  <Alert variant="destructive" className="border-red-200 bg-red-50">
                    <AlertDescription className="text-red-700">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Loading Animation */}
        {loading && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-6">
              <div className="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-900">Processing article...</p>
              <p className="text-gray-600">This may take a few seconds</p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="space-y-8">
            
            {/* Success Banner */}
            <div className="text-center">
              <div className="inline-flex items-center bg-green-50 border border-green-200 text-green-800 px-6 py-3 rounded-full">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Article processed successfully • {result.word_count?.toLocaleString()} words • {calculateReadingTime(result.word_count)} min read
              </div>
            </div>

            {/* Language Toggle */}
            <div className="flex justify-center">
              <div className="bg-white rounded-full p-1 shadow-md border">
                <Button
                  variant={!showUrdu ? "default" : "ghost"}
                  onClick={() => setShowUrdu(false)}
                  className="rounded-full px-6"
                  size="sm"
                >
                  English
                </Button>
                <Button
                  variant={showUrdu ? "default" : "ghost"}
                  onClick={() => setShowUrdu(true)}
                  className="rounded-full px-6"
                  size="sm"
                >
                  اردو
                </Button>
              </div>
            </div>

            {/* Article Title */}
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 leading-tight">
                {showUrdu && result.title_urdu ? result.title_urdu : result.title}
              </h2>
              {result.metadata?.author && (
                <p className="text-gray-600">by {result.metadata.author}</p>
              )}
            </div>

            {/* Main Summary Card */}
            <Card className="shadow-xl border-0 bg-white">
              <CardHeader className="text-center pb-4">
                <CardTitle className="text-xl">
                  {showUrdu ? "خلاصہ" : "Summary"}
                </CardTitle>
              </CardHeader>
              <CardContent className="px-8 pb-8">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 mb-6">
                  <div className="prose prose-lg max-w-none">
                    <p className="text-gray-800 leading-relaxed m-0 text-lg">
                      {showUrdu ? result.ai_summary_urdu : result.ai_summary}
                    </p>
                  </div>
                </div>

                {/* Stats Row */}
                <div className="flex justify-center gap-8 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {Math.round((result.summary_stats?.summary_sentences || 0) / (result.summary_stats?.original_sentences || 1) * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">
                      {showUrdu ? "کمپریشن" : "Compression"}
                    </div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {Math.max(0, calculateReadingTime(result.word_count) - calculateReadingTime(result.ai_summary?.split(' ').length || 0))}
                    </div>
                    <div className="text-sm text-gray-600">
                      {showUrdu ? "منٹ بچے" : "Min Saved"}
                    </div>
                  </div>
                  {result.translation_stats && (
                    <div>
                      <div className="text-2xl font-bold text-purple-600">
                        {result.translation_stats.coverage || 0}%
                      </div>
                      <div className="text-sm text-gray-600">
                        {showUrdu ? "ترجمہ" : "Translation"}
                      </div>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex justify-center gap-4 mt-8">
                  <Button
                    variant="outline"
                    onClick={() => navigator.clipboard.writeText(showUrdu ? result.ai_summary_urdu : result.ai_summary)}
                    className="px-6"
                  >
                    {showUrdu ? "کاپی کریں" : "Copy Summary"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => window.open(result.url, '_blank')}
                    className="px-6"
                  >
                    {showUrdu ? "اصل مضمون" : "Read Original"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Translation Quality Warning */}
            {showUrdu && result.translation_stats && result.translation_stats.coverage < 70 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-amber-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="text-amber-800 text-sm">
                    Translation quality: {result.translation_stats.coverage}%. Some technical terms remain in English.
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

      </main>

      {/* Minimal Footer */}
      <footer className="text-center py-8 text-gray-500 text-sm">
        <p>Powered by AI • Built for Assignment 2</p>
      </footer>
    </div>
  );
}