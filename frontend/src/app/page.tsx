'use client';

// This is our main component - like the main page of our website
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function BlogScraper() {
  // These are "state" variables - they remember things
  const [url, setUrl] = useState('');           // The URL user types
  const [result, setResult] = useState(null);   // The scraping result
  const [loading, setLoading] = useState(false); // Is it loading?
  const [error, setError] = useState('');       // Any error messages

  // This function runs when user clicks "Scrape Blog"
  const handleScrape = async () => {
    // Basic validation
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    // Clear previous results
    setError('');
    setResult(null);
    setLoading(true);

    try {
      console.log('🚀 Sending request to Python API...');
      
      // This talks to your Python backend!
      const response = await fetch('http://localhost:8000/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
      });

      const data = await response.json();
      console.log('📦 Got response from Python:', data);

      if (data.success) {
        setResult(data);
        console.log('✅ Success! Got blog content');
      } else {
        setError(data.error || 'Failed to scrape blog');
        console.log('❌ Error:', data.error);
      }

    } catch (err) {
      console.error('🔥 Network error:', err);
      setError('Could not connect to the scraper service. Is your Python server running?');
    } finally {
      setLoading(false);
    }
  };

  // This is what gets displayed on the webpage
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🤖 Blog Scraper
          </h1>
          <p className="text-gray-600">
            Enter a blog URL and I'll extract the content for you!
          </p>
        </div>

        {/* Input Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Enter Blog URL</CardTitle>
            <CardDescription>
              Paste any blog URL and click "Scrape Blog" to extract its content
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex space-x-2">
              <Input
                type="url"
                placeholder="https://example.com/blog-post"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Button 
                onClick={handleScrape}
                disabled={loading}
                className="min-w-[120px]"
              >
                {loading ? (
                  <span className="flex items-center space-x-2">
                    <span className="animate-spin">🔄</span>
                    <span>Scraping...</span>
                  </span>
                ) : (
                  '🚀 Scrape Blog'
                )}
              </Button>
            </div>
            
            {/* Quick test buttons */}
            <div className="flex space-x-2 text-sm">
              <span className="text-gray-500">Quick test:</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setUrl('https://example.com')}
              >
                Example.com
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setUrl('https://httpbin.org/html')}
              >
                Test HTML
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <Alert className="mb-8 border-red-200 bg-red-50">
            <AlertDescription className="text-red-700">
              ❌ {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="text-green-600">
                ✅ Scraping Successful!
              </CardTitle>
              <CardDescription>
                Here's what I found from: {result.url}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              
              {/* Title */}
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">📰 Title:</h3>
                <p className="bg-blue-50 p-3 rounded border">
                  {result.title}
                </p>
              </div>

              {/* Word Count */}
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">📊 Statistics:</h3>
                <p className="text-sm text-gray-600">
                  Word count: <span className="font-medium">{result.word_count}</span> words
                </p>
              </div>

              {/* Content Preview */}
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">📄 Content Preview:</h3>
                <div className="bg-gray-50 p-4 rounded border max-h-60 overflow-y-auto">
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {result.content.substring(0, 500)}
                    {result.content.length > 500 && '...'}
                  </p>
                </div>
              </div>

              {/* Future Features Placeholder */}
              <div className="bg-yellow-50 p-4 rounded border">
                <p className="text-sm text-yellow-700">
                  🚧 <strong>Coming Next:</strong> AI Summary & Urdu Translation
                </p>
              </div>

            </CardContent>
          </Card>
        )}

        {/* Instructions */}
        <Card className="mt-8 bg-blue-50">
          <CardContent className="pt-6">
            <h3 className="font-semibold mb-2">🎯 How it works:</h3>
            <ol className="text-sm text-gray-700 space-y-1">
              <li>1. You enter a blog URL</li>
              <li>2. Next.js sends the URL to your Python backend</li>
              <li>3. Python scrapes the website and extracts content</li>
              <li>4. The results are displayed here beautifully!</li>
            </ol>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}