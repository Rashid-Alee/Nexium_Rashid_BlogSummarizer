'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function BlogScraper() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Calculate reading time (average 200 words per minute)
  const calculateReadingTime = (wordCount) => {
    if (!wordCount) return 0;
    return Math.ceil(wordCount / 200);
  };

  // Calculate time saved
  const calculateTimeSaved = (originalWords, summaryWords) => {
    const originalTime = calculateReadingTime(originalWords);
    const summaryTime = calculateReadingTime(summaryWords);
    return Math.max(0, originalTime - summaryTime);
  };

  const handleScrape = async () => {
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    setError('');
    setResult(null);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to scrape blog');
      }
    } catch (err) {
      setError('Could not connect to the scraper service.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Clean Header */}
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-6 py-6 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Blog Summarizer
          </h1>
          <p className="text-gray-600">
            Get the key points from any article in seconds
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        
        {/* Input Section */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex gap-3">
                <Input
                  type="url"
                  placeholder="Paste article URL here..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={handleScrape}
                  disabled={loading}
                  className="px-6"
                >
                  {loading ? 'Analyzing...' : 'Summarize'}
                </Button>
              </div>
              
              <div className="flex gap-2 text-sm">
                <span className="text-gray-500">Try:</span>
                <button
                  onClick={() => setUrl('https://en.wikipedia.org/wiki/Artificial_intelligence')}
                  className="text-blue-600 hover:underline"
                >
                  AI Article
                </button>
                <button
                  onClick={() => setUrl('https://httpbin.org/html')}
                  className="text-blue-600 hover:underline"
                >
                  Test Page
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <Alert className="mb-8 border-red-200 bg-red-50">
            <AlertDescription className="text-red-700">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            
            {/* Time Saved Banner */}
            {result.word_count > 0 && (
              <div className="text-center">
                <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
                  <span className="mr-2">⏱️</span>
                  Saved you {calculateTimeSaved(result.word_count, result.ai_summary?.split(' ').length || 0)} minutes of reading
                </div>
              </div>
            )}

            {/* AI Summary - Main Focus */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl">Summary</CardTitle>
                  <div className="text-sm text-gray-500">
                    {calculateReadingTime(result.ai_summary?.split(' ').length || 0)} min read
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-gray-800 leading-relaxed text-lg">
                    {result.ai_summary}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Article Title & Source */}
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 leading-tight">
                      {result.title}
                    </h3>
                  </div>
                  
                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>📖 {calculateReadingTime(result.word_count)} min read</span>
                      {result.metadata?.author && (
                        <span>✍️ {result.metadata.author}</span>
                      )}
                      {result.metadata?.publish_date && (
                        <span>📅 {new Date(result.metadata.publish_date).toLocaleDateString()}</span>
                      )}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(result.url, '_blank')}
                      className="shrink-0"
                    >
                      Read Full Article
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Insights (Only if Useful) */}
            {result.summary_stats && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <span>🎯</span>
                      <span>
                        Condensed to {Math.round((result.summary_stats.summary_sentences / result.summary_stats.original_sentences) * 100)}% of original
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span>💡</span>
                      <span>
                        {result.summary_stats.important_words_found} key concepts identified
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Content Preview (Collapsible) */}
            <details className="group">
              <summary className="cursor-pointer bg-white border rounded-lg p-4 hover:bg-gray-50 flex items-center justify-between">
                <span className="font-medium">Preview full content</span>
                <span className="text-gray-400 group-open:rotate-180 transition-transform">▼</span>
              </summary>
              
              <Card className="mt-2">
                <CardContent className="pt-6">
                  <div className="bg-gray-50 border rounded p-4 max-h-60 overflow-y-auto">
                    <p className="text-gray-700 text-sm leading-relaxed">
                      {result.content?.substring(0, 1000) || 'No content available'}
                      {result.content?.length > 1000 && '...'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </details>
          </div>
        )}

      </main>

      {/* Simple Footer */}
      <footer className="mt-16 py-8 text-center text-sm text-gray-500 border-t">
        <div className="max-w-4xl mx-auto px-6">
          <p>AI-powered summarization • Built with Python & Next.js</p>
        </div>
      </footer>
    </div>
  );
}