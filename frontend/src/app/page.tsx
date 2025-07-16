"use client"

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Search, Sparkles, Globe, Zap, Database, Languages, Wifi, WifiOff, CheckCircle, Brain, Cpu, Eye, Target } from 'lucide-react';

import { api } from '@/lib/api';

interface NotificationDetails {
  message?: string;
  responseTime?: string | number;
  supabase?: string;
  mongodb?: string;
  details?: string;
}

interface Notification {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  details?: NotificationDetails | string | null;
}

interface ProgressStage {
  key: string;
  label: string;
  progress: number;
  icon: string;
}

interface FloatingElement {
  id: number;
  x: number;
  y: number;
  size: number;
  delay: number;
  duration: number;
  color: string;
}

interface MousePosition {
  x: number;
  y: number;
}

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  cached?: boolean;
  performance?: {
    response_time_ms?: number;
  };
  database?: any;
}

interface ResultData {
  title: string;
  title_urdu?: string;
  ai_summary: string;
  ai_summary_urdu: string;
  word_count?: number;
  author?: string;
  publish_date?: string;
  description?: string;
  url?: string;
  summary_stats?: {
    summary_sentences?: number;
    compression_ratio?: string;
  };
}

export default function SummaIQ() {
  // Welcome Screen State
  const [showWelcome, setShowWelcome] = useState(true);
  const [welcomeStage, setWelcomeStage] = useState<'intro' | 'brand' | 'tagline' | 'enter'>('intro');
  
  const [url, setUrl] = useState<string>('');
  const [result, setResult] = useState<ResultData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [showUrdu, setShowUrdu] = useState<boolean>(false);
  const [notification, setNotification] = useState<Notification | null>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [loadingStage, setLoadingStage] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [loadingSteps, setLoadingSteps] = useState<string[]>([]);
  const [isClient, setIsClient] = useState<boolean>(false);
  const [mousePosition, setMousePosition] = useState<MousePosition>({ x: 0, y: 0 });
  const [floatingElements, setFloatingElements] = useState<FloatingElement[]>([]);

  //PROGRESS STAGES
  const progressStages: ProgressStage[] = [
    { key: 'fetching', label: 'Fetching content...', progress: 20, icon: '🌐' },
    { key: 'extracting', label: 'Extracting text...', progress: 40, icon: '📝' },
    { key: 'summarizing', label: 'AI summarizing...', progress: 60, icon: '🧠' },
    { key: 'translating', label: 'Translating to Urdu...', progress: 80, icon: '🌍' },
    { key: 'saving', label: 'Saving to database...', progress: 90, icon: '💾' },
    { key: 'complete', label: 'Analysis complete!', progress: 100, icon: '✅' }
  ];

  // WELCOME SCREEN ANIMATION SEQUENCE
  useEffect(() => {
    if (showWelcome) {
      const sequence = [
        { stage: 'intro' as const, duration: 1000 },
        { stage: 'brand' as const, duration: 2000 },
        { stage: 'tagline' as const, duration: 2000 },
        { stage: 'enter' as const, duration: 1000 }
      ];
      
      let currentIndex = 0;
      const runSequence = () => {
        if (currentIndex < sequence.length) {
          setWelcomeStage(sequence[currentIndex].stage);
          setTimeout(() => {
            currentIndex++;
            runSequence();
          }, sequence[currentIndex].duration);
        } else {
          // Auto-proceed to main app after welcome sequence
          setTimeout(() => {
            setShowWelcome(false);
            checkApiConnection();
          }, 1000);
        }
      };
      
      runSequence();
    }
  }, [showWelcome]);

  // Skip welcome screen
  const skipWelcome = () => {
    setShowWelcome(false);
    checkApiConnection();
  };

  const simulateProgress = () => {
    setProgress(0);
    setLoadingSteps([]);
    
    progressStages.forEach((stage, index) => {
      setTimeout(() => {
        setLoadingStage(stage.key);
        setProgress(stage.progress);
        setLoadingSteps(prev => [...prev, stage.key]);
      }, index * 800 + Math.random() * 400);
    });
  };

  // Mouse tracking for interactive effects
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    setIsClient(true);
    
    // Create floating elements
    const elements: FloatingElement[] = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 20 + 10,
      delay: Math.random() * 5,
      duration: Math.random() * 10 + 10,
      color: ['blue', 'purple', 'indigo', 'pink', 'cyan'][Math.floor(Math.random() * 5)]
    }));
    setFloatingElements(elements);
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

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setNotification(null);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const showNotification = (type: Notification['type'], message: string, details: NotificationDetails | string | null = null) => {
    setNotification({ type, message, details });
  };

  const calculateReadingTime = (wordCount?: number): number => {
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

    simulateProgress();

    try {
      console.log(`🚀 Starting blog scrape for: ${url}`);
      
      const data: ApiResponse = await api.scrapeBlog(url);

      if (data.success) {
        setProgress(100);
        setLoadingStage('complete');
        setResult(data.data);
        
        if (data.cached) {
          showNotification('info', 'Retrieved from cache', {
            message: 'This article was previously analyzed',
            responseTime: data.performance?.response_time_ms || 'Unknown'
          });
        } else {
          showNotification('success', 'Article analyzed successfully!', {
            message: 'Summary and translation completed perfectly',
            supabase: 'Summary saved ✅',
            mongodb: 'Content saved ✅'
          });
        }
      } else {
        setError(data.error || 'Failed to analyze the blog post');
        showNotification('error', 'Analysis failed', {
          message: data.error || 'Unknown error occurred'
        });
      }
    } catch (error) {
      console.error('❌ Error during blog scraping:', error);
      setError('Network error: Could not connect to the API');
      showNotification('error', 'Connection failed', {
        message: 'Could not connect to the analysis service'
      });
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setLoadingStage('');
        setLoadingSteps([]);
      }, 2000);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleScrape();
    }
  };

  // WELCOME SCREEN COMPONENT
  if (showWelcome) {
    return (
      <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center overflow-hidden z-50" suppressHydrationWarning={true}>
        
        {/* Animated Background */}
        {isClient && (
          <div className="absolute inset-0 overflow-hidden">
            {floatingElements.map((element) => (
              <div
                key={element.id}
                className={`absolute rounded-full bg-gradient-to-r from-${element.color}-400 to-${element.color}-600 opacity-20 blur-xl animate-pulse`}
                style={{
                  left: `${element.x}%`,
                  top: `${element.y}%`,
                  width: `${element.size}px`,
                  height: `${element.size}px`,
                  animationDelay: `${element.delay}s`,
                  animationDuration: `${element.duration}s`,
                }}
              />
            ))}
          </div>
        )}

        {/* Welcome Content */}
        <div className="relative z-10 text-center space-y-8 px-4"> {/* Added px-4 for mobile padding */}
          
          {/* Intro Stage */}
          {welcomeStage === 'intro' && (
            <div className="animate-in fade-in duration-1000">
              <div className="text-xl md:text-2xl text-gray-300 mb-4">Welcome to</div> {/* Adjusted font size */}
            </div>
          )}

          {/* Brand Stage */}
          {welcomeStage === 'brand' && (
            <div className="animate-in fade-in slide-in-from-bottom-8 duration-1000">
              <div className="text-xl md:text-2xl text-gray-300 mb-4">Welcome to</div> {/* Adjusted font size */}
              <h1 className="text-6xl sm:text-8xl md:text-9xl font-bold"> {/* Adjusted font size for mobile */}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 animate-pulse">
                  SummaIQ
                </span>
              </h1>
              <div className="w-32 h-1 bg-gradient-to-r from-cyan-400 to-purple-400 mx-auto mt-6 rounded-full"></div>
            </div>
          )}

          {/* Tagline Stage */}
          {welcomeStage === 'tagline' && (
            <div className="animate-in fade-in slide-in-from-bottom-8 duration-1000">
              <div className="text-xl md:text-2xl text-gray-300 mb-4">Welcome to</div> {/* Adjusted font size */}
              <h1 className="text-6xl sm:text-8xl md:text-9xl font-bold"> {/* Adjusted font size for mobile */}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 animate-pulse">
                  SummaIQ
                </span>
              </h1>
              <div className="w-32 h-1 bg-gradient-to-r from-cyan-400 to-purple-400 mx-auto mt-6 rounded-full"></div>
              <p className="text-base md:text-xl text-gray-300 mt-8 max-w-2xl mx-auto leading-relaxed"> {/* Adjusted font size */}
                Your intelligent content companion. Turn lengthy articles into clear insights with smart analysis and instant translation.
              </p>
            </div>
          )}

          {/* Enter Stage */}
          {welcomeStage === 'enter' && (
            <div className="animate-in fade-in slide-in-from-bottom-8 duration-1000">
              <div className="text-xl md:text-2xl text-gray-300 mb-4">Welcome to</div> {/* Adjusted font size */}
              <h1 className="text-6xl sm:text-8xl md:text-9xl font-bold"> {/* Adjusted font size for mobile */}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 animate-pulse">
                  SummaIQ
                </span>
              </h1>
              <div className="w-32 h-1 bg-gradient-to-r from-cyan-400 to-purple-400 mx-auto mt-6 rounded-full"></div>
              <p className="text-base md:text-xl text-gray-300 mt-8 max-w-2xl mx-auto leading-relaxed"> {/* Adjusted font size */}
                Your intelligent content companion. Turn lengthy articles into clear insights with smart analysis and instant translation.
              </p>
              
              <div className="mt-12 space-y-4">
                <div className="text-gray-400">Get ready to explore...</div>
                <div className="flex items-center justify-center gap-4">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
                  <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
                </div>
              </div>
            </div>
          )}

          {/* Skip Button */}
          <button
            onClick={skipWelcome}
            className="absolute bottom-4 right-4 text-gray-400 hover:text-white transition-colors duration-300 text-sm" // Adjusted position
          >
            Skip intro →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden" suppressHydrationWarning={true}>
      
      {/* Animated Background with Floating Elements */}
      {isClient && (
        <div className="absolute inset-0 overflow-hidden">
          {floatingElements.map((element) => (
            <div
              key={element.id}
              className={`absolute rounded-full bg-gradient-to-r from-${element.color}-400 to-${element.color}-600 opacity-20 blur-xl animate-pulse`}
              style={{
                left: `${element.x}%`,
                top: `${element.y}%`,
                width: `${element.size}px`,
                height: `${element.size}px`,
                animationDelay: `${element.delay}s`,
                animationDuration: `${element.duration}s`,
              }}
            />
          ))}
        </div>
      )}

      {isClient && (
        <div 
          className="fixed pointer-events-none z-0 opacity-30"
          style={{
            left: mousePosition.x - 100,
            top: mousePosition.y - 100,
            transition: 'all 0.3s ease-out'
          }}
        >
          <div className="w-48 h-48 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full blur-3xl"></div>
        </div>
      )}

      {/*Grid Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="w-full h-full" style={{
          backgroundImage: `
            linear-gradient(rgba(139, 92, 246, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(139, 92, 246, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px'
        }}></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        
        <div className="text-center mb-8 pt-12 sm:pt-0"> {/* Added pt-12 for mobile to push content down */}
          <h1 className="text-4xl md:text-5xl font-bold">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400">
              SummaIQ
            </span>
          </h1>
          <p className="text-gray-400 mt-2">Your intelligent content companion</p>
        </div>

        {/* Adjusted positioning for mobile to prevent overlap */}
        <div className="absolute top-4 right-4 z-20 sm:top-4 sm:right-4"> 
          <div className={`flex items-center gap-3 px-4 py-2 sm:px-6 sm:py-3 rounded-2xl backdrop-blur-lg border-2 transition-all duration-500 ${
            apiStatus === 'connected' 
              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400/50 shadow-lg shadow-emerald-500/20' 
              : apiStatus === 'disconnected'
              ? 'bg-red-500/20 text-red-300 border-red-400/50 shadow-lg shadow-red-500/20'
              : 'bg-amber-500/20 text-amber-300 border-amber-400/50 shadow-lg shadow-amber-500/20'
          }`}>
            <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${
              apiStatus === 'connected' ? 'bg-emerald-400 animate-pulse' :
              apiStatus === 'disconnected' ? 'bg-red-400' : 'bg-amber-400 animate-pulse'
            }`}></div>
            <span className="font-semibold text-sm sm:text-base"> {/* Adjusted font size */}
              {apiStatus === 'connected' ? 'System Online' : 
               apiStatus === 'disconnected' ? 'System Offline' : 'Connecting...'}
            </span>
          </div>
        </div>

        {/*Notifications */}
        {notification && (
          <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 max-w-sm w-full px-4 sm:max-w-md"> {/* Adjusted max-width for mobile */}
            <div className={`p-4 rounded-2xl backdrop-blur-lg border-2 shadow-2xl transition-all duration-500 ${ // Adjusted padding
              notification.type === 'success' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-400/30 shadow-emerald-500/20' :
              notification.type === 'error' ? 'bg-red-500/10 text-red-300 border-red-400/30 shadow-red-500/20' :
              notification.type === 'warning' ? 'bg-amber-500/10 text-amber-300 border-amber-400/30 shadow-amber-500/20' :
              'bg-blue-500/10 text-blue-300 border-blue-400/30 shadow-blue-500/20'
            }`}>
              <div className="font-bold text-base sm:text-lg">{notification.message}</div> {/* Adjusted font size */}
              {notification.details && (
                <div className="text-xs sm:text-sm mt-2 opacity-90"> {/* Adjusted font size */}
                  {typeof notification.details === 'string' ? notification.details : 
                   `${(notification.details as NotificationDetails).message || ''} ${(notification.details as NotificationDetails).responseTime ? `(${(notification.details as NotificationDetails).responseTime}ms)` : ''}`
                  }
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Hero Section */}
        <div className="text-center mb-12 sm:mb-20 space-y-6 sm:space-y-8"> {/* Adjusted margin and space */}
          <div className="inline-flex items-center gap-2 sm:gap-3 bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-lg border border-purple-400/30 rounded-full px-4 py-2 sm:px-8 sm:py-4 text-purple-300 shadow-lg shadow-purple-500/20"> {/* Adjusted padding and gap */}
            <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" /> {/* Adjusted icon size */}
            <span className="text-base sm:text-lg font-bold">Smart Content Analysis</span> {/* Adjusted font size */}
          </div>
          
          <h2 className="text-3xl md:text-6xl lg:text-7xl font-bold leading-tight"> {/* Adjusted font size for mobile */}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400">
              Turn Complex
            </span>
            <br />
            <span className="text-xl md:text-5xl lg:text-6xl text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-blue-400 to-cyan-400"> {/* Adjusted font size for mobile */}
              Articles into Insights
            </span>
          </h2>
          
          <p className="text-base md:text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed px-4"> {/* Adjusted font size */}
            Get clear summaries, key insights, and instant translations. 
            SummaIQ makes complex content simple and actionable in seconds.
          </p>

          {/* Feature Showcase */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mt-8 md:mt-16 max-w-4xl mx-auto px-4"> {/* Changed to grid-cols-2 for mobile */}
            {[
              { icon: <Eye className="w-6 h-6 sm:w-8 sm:h-8" />, title: "Smart Reading", desc: "Extracts key information", color: "from-cyan-400 to-blue-500" },
              { icon: <Brain className="w-6 h-6 sm:w-8 sm:h-8" />, title: "Quick Summary", desc: "Gets the main points", color: "from-purple-400 to-pink-500" },
              { icon: <Globe className="w-6 h-6 sm:w-8 sm:h-8" />, title: "Easy Translation", desc: "Works in urdu and English Language", color: "from-green-400 to-emerald-500" },
              { icon: <Zap className="w-6 h-6 sm:w-8 sm:h-8" />, title: "Super Fast", desc: "Results in under 30 seconds", color: "from-yellow-400 to-orange-500" }
            ].map((feature, index) => (
              <div key={index} className="group relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative bg-gray-900/50 backdrop-blur-lg border border-gray-700/50 rounded-2xl p-4 sm:p-6 hover:border-purple-400/50 transition-all duration-300"> {/* Adjusted padding */}
                  <div className={`w-12 h-12 sm:w-16 sm:h-16 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center mb-2 sm:mb-4 mx-auto`}> {/* Adjusted size */}
                    {feature.icon}
                  </div>
                  <h3 className="text-base sm:text-lg font-bold text-white mb-1 sm:mb-2">{feature.title}</h3> {/* Adjusted font size */}
                  <p className="text-xs sm:text-sm text-gray-400">{feature.desc}</p> {/* Adjusted font size */}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/*Input Terminal */}
        <div className="max-w-2xl mx-auto mb-12 md:mb-20 px-4">
          <div className="group relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 rounded-3xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-gray-900/80 backdrop-blur-2xl border border-gray-700/50 rounded-3xl shadow-2xl">
              <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-6 sm:p-8 border-b border-gray-700/50 rounded-t-3xl"> {/* Adjusted padding */}
                <h3 className="text-2xl sm:text-3xl font-bold text-white text-center mb-1 sm:mb-2"> {/* Adjusted font size */}
                  Start Here
                </h3>
                <p className="text-sm sm:text-base text-gray-300 text-center">Paste any blog URL to get started</p> {/* Adjusted font size */}
              </div>
              <div className="p-6 sm:p-8 space-y-6 sm:space-y-8"> {/* Adjusted padding and space */}
                <div className="space-y-4 sm:space-y-6"> {/* Adjusted space */}
                  <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
                    <div className="relative">
                      <Input
                        type="url"
                        placeholder="https://target-blog.com/article"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyPress={handleKeyPress}
                        className="h-14 pl-12 pr-4 text-base sm:h-16 sm:pl-16 sm:pr-6 sm:text-lg bg-gray-800/80 border-2 border-gray-600/50 focus:border-cyan-400 text-white placeholder-gray-400 rounded-2xl backdrop-blur-lg transition-all duration-300 shadow-lg" // Adjusted size and padding
                        required
                      />
                      <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-cyan-400 sm:left-6 sm:w-6 sm:h-6" /> {/* Adjusted icon size and position */}
                    </div>
                  </div>

                  {/* Quick Examples */}
                  <div className="space-y-3 sm:space-y-4"> {/* Adjusted space */}
                    <div className="text-center">
                      <h4 className="text-base sm:text-lg font-bold text-cyan-400 mb-3 sm:mb-4">⚡ Try These Examples</h4>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4"> 
                      {[
                        { title: "🚀 Tech News", url: "https://blog.google/technology/ai/", desc: "Google Tech Blog", gradient: "from-blue-500 to-cyan-500" },
                        { title: "💼 Business Tips", url: "https://hbr.org/topic/strategy", desc: "Harvard Business Review", gradient: "from-purple-500 to-pink-500" },
                        { title: "✨ Life Hacks", url: "https://www.lifehack.org/articles/lifestyle", desc: "Productivity Tips", gradient: "from-green-500 to-emerald-500" },
                        { title: "📈 Marketing Ideas", url: "https://blog.hubspot.com/marketing", desc: "HubSpot Insights", gradient: "from-orange-500 to-red-500" }
                      ].map((example, index) => (
                        <button
                          key={index}
                          onClick={() => setUrl(example.url)}
                          className="group relative overflow-hidden"
                        >
                          <div className={`absolute inset-0 bg-gradient-to-r ${example.gradient} opacity-10 group-hover:opacity-20 transition-opacity duration-300`}></div>
                          <div className="relative p-3 md:p-4 bg-gray-800/60 border border-gray-600/50 rounded-xl hover:border-cyan-400/50 transition-all duration-300 backdrop-blur-lg">
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-gradient-to-r ${example.gradient} flex items-center justify-center text-white font-bold text-sm sm:text-base`}> {/* Adjusted size and font */}
                                {example.title.split(' ')[0]}
                              </div>
                              <div className="text-left">
                                <div className="font-bold text-white group-hover:text-cyan-400 transition-colors text-sm sm:text-base"> {/* Adjusted font size */}
                                  {example.title}
                                </div>
                                <div className="text-xs sm:text-sm text-gray-400 group-hover:text-gray-300"> {/* Adjusted font size */}
                                  {example.desc}
                                </div>
                              </div>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                    <Button
                      onClick={handleScrape}
                      disabled={!url || loading || apiStatus !== 'connected'}
                      className="relative w-full h-14 text-lg font-bold bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed sm:h-16 sm:text-xl" // Adjusted size and font
                    >
                      <span className="flex items-center gap-3">
                        {loading ? (
                          <>
                            <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin sm:w-6 sm:h-6"></div> {/* Adjusted size */}
                            Processing...
                          </>
                        ) : (
                          <>
                            <Cpu className="w-5 h-5 sm:w-6 sm:h-6" /> {/* Adjusted size */}
                            Start Analysis
                          </>
                        )}
                      </span>
                    </Button>
                  </div>
                </div>

                {/* Feature Pills */}
                <div className="flex flex-wrap gap-2 sm:gap-3 justify-center pt-4 sm:pt-6 border-t border-gray-700/50"> 
                  {[
                    { icon: Globe, label: 'Smart Reading', gradient: 'from-cyan-500 to-blue-500' },
                    { icon: Brain, label: 'Quick Summary', gradient: 'from-purple-500 to-pink-500' },
                    { icon: Languages, label: 'Easy Translation', gradient: 'from-green-500 to-emerald-500' },
                    { icon: Database, label: 'Secure Storage', gradient: 'from-orange-500 to-red-500' },
                  ].map((feature, index) => {
                    const IconComponent = feature.icon;
                    return (
                      <div
                        key={index}
                        className={`flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r ${feature.gradient} bg-opacity-20 border border-gray-600/50 rounded-full text-xs text-white hover:bg-opacity-30 transition-all duration-300 cursor-pointer backdrop-blur-lg sm:px-4 sm:py-2 sm:text-sm`} // Adjusted padding and font size
                      >
                        <IconComponent className="w-3 h-3 sm:w-4 sm:h-4" /> {/* Adjusted icon size */}
                        <span className="font-medium">{feature.label}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Scanner */}
        {loading && (
          <div className="max-w-2xl mx-auto mb-8 sm:mb-12 px-4">
            <div className="group relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 rounded-3xl blur opacity-50 animate-pulse"></div>
              <div className="relative bg-gray-900/90 backdrop-blur-2xlborder border-gray-700/50 rounded-3xl shadow-2xl">
                <div className="p-6 sm:p-8"> {/* Adjusted padding */}
                  <div className="space-y-4 sm:space-y-6"> {/* Adjusted space */}
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-2 sm:gap-0"> {/* Adjusted for stacking on mobile */}
                      <h3 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2 sm:gap-3"> {/* Adjusted font size */}
                        <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-full flex items-center justify-center"> {/* Adjusted size */}
                          <Cpu className="w-4 h-4 sm:w-5 sm:h-5 text-white animate-pulse" /> {/* Adjusted size */}
                        </div>
                        SummaIQ is Processing...
                      </h3>
                      <div className="text-xl sm:text-2xl font-bold text-cyan-400"> {/* Adjusted font size */}
                        {progress}%
                      </div>
                    </div>

                    <div className="relative">
                      <div className="w-full bg-gray-800 rounded-full h-3 sm:h-4 overflow-hidden"> {/* Adjusted height */}
                        <div 
                          className="h-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 rounded-full transition-all duration-700 ease-out relative"
                          style={{ width: `${progress}%` }}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/5 animate-pulse"></div>
                          <div className="absolute top-0 right-0 w-1.5 h-full bg-white/50 animate-pulse sm:w-2"></div> {/* Adjusted width */}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 sm:gap-3"> {/* Adjusted gap */}
                      <div className="w-2.5 h-2.5 bg-cyan-400 rounded-full animate-pulse sm:w-3 sm:h-3"></div> {/* Adjusted size */}
                      <span className="text-base sm:text-lg text-cyan-300 font-bold"> {/* Adjusted font size */}
                        {progressStages.find(s => s.key === loadingStage)?.label || 'Getting started...'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4"> {/* Changed to grid-cols-1 for mobile */}
                      {progressStages.map((stage) => (
                        <div 
                          key={stage.key}
                          className={`flex items-center gap-2 sm:gap-3 text-sm p-3 rounded-xl border transition-all duration-500 ${ // Adjusted padding and font size
                            loadingSteps.includes(stage.key) 
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400/50' 
                              : loadingStage === stage.key
                              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50'
                              : 'bg-gray-800/50 text-gray-500 border-gray-600/50'
                          }`}
                        >
                          <div className="text-base sm:text-lg">{stage.icon}</div>
                          <div className={`w-2 h-2 rounded-full ${
                            loadingSteps.includes(stage.key) 
                              ? 'bg-emerald-400' 
                              : loadingStage === stage.key
                              ? 'bg-cyan-400 animate-pulse'
                              : 'bg-gray-600'
                          }`}></div>
                          <span className="font-medium">{stage.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 px-4"> 
            <div className="group relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl blur opacity-50"></div>
              <div className="relative bg-red-500/10 backdrop-blur-lg border border-red-400/30 rounded-2xl p-4 sm:p-6"> {/* Adjusted padding */}
                <div className="text-red-300 font-bold text-base sm:text-lg flex items-center gap-2 sm:gap-3"> {/* Adjusted font size and gap */}
                  <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center sm:w-6 sm:h-6"> {/* Adjusted size */}
                    <span className="text-white text-xs sm:text-sm">!</span> {/* Adjusted font size */}
                  </div>
                  ERROR: {error}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* RESULTS SECTION */}
        {result && (
          <div className="max-w-7xl mx-auto space-y-8 sm:space-y-12 px-4"> {/* Adjusted space and added px-4 */}
            
            <div className="text-center space-y-4 sm:space-y-6"> {/* Adjusted space */}
              <div className="inline-flex items-center gap-2 sm:gap-3 bg-emerald-500/20 border border-emerald-400/30 rounded-full px-4 py-2 sm:px-6 sm:py-3 text-emerald-300 backdrop-blur-lg"> {/* Adjusted padding and gap */}
                <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5" /> {/* Adjusted icon size */}
                <span className="text-base sm:text-lg font-bold">SummaIQ Analysis Complete</span> {/* Adjusted font size */}
              </div>
              <h2 className="text-3xl sm:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400"> {/* Adjusted font size */}
                Your Content Summary
              </h2>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 mb-8 sm:mb-16 px-0">
              {[
                { 
                  label: 'Total Words', 
                  value: result.word_count ? result.word_count.toLocaleString() : 'N/A', 
                  icon: '📝',
                  gradient: 'from-cyan-400 to-blue-500',
                  bg: 'from-cyan-500/20 to-blue-500/20'
                },
                { 
                  label: 'Read Time', 
                  value: `${calculateReadingTime(result.word_count)} min`, 
                  icon: '⏱️',
                  gradient: 'from-purple-400 to-pink-500',
                  bg: 'from-purple-500/20 to-pink-500/20'
                },
                { 
                  label: 'Summary', 
                  value: result.summary_stats?.summary_sentences || 'N/A', 
                  icon: '📊',
                  gradient: 'from-green-400 to-emerald-500',
                  bg: 'from-green-500/20 to-emerald-500/20'
                },
                { 
                  label: 'Compression', 
                  value: result.summary_stats?.compression_ratio || 'N/A', 
                  icon: '⚡',
                  gradient: 'from-orange-400 to-red-500',
                  bg: 'from-orange-500/20 to-red-500/20'
                }
              ].map((stat, index) => (
                <div key={index} className="group relative">
                  <div className={`absolute -inset-1 bg-gradient-to-r ${stat.gradient} rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200`}></div>
                  <div className={`relative bg-gradient-to-br ${stat.bg} backdrop-blur-lg border border-gray-700/50 rounded-2xl p-3 sm:p-4 md:p-6 hover:border-cyan-400/50 transition-all duration-300`}> {/* Adjusted padding */}
                    <div className="text-center space-y-1 sm:space-y-2 md:space-y-3"> {/* Adjusted space */}
                      <div className="text-2xl sm:text-3xl md:text-4xl">{stat.icon}</div> {/* Adjusted font size */}
                      <div className={`text-xl sm:text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r ${stat.gradient}`}> {/* Adjusted font size */}
                        {stat.value}
                      </div>
                      <div className="text-xs sm:text-sm text-gray-300 font-medium">{stat.label}</div> {/* Adjusted font size */}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Main Results Panel */}
            <div className="group relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 rounded-3xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
              <div className="relative bg-gray-900/80 backdrop-blur-2xl border border-gray-700/50 rounded-3xl shadow-2xl overflow-hidden">
                <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 p-5 sm:p-6 md:p-8 border-b border-gray-700/50"> {/* Adjusted padding */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4"> {/* Adjusted for stacking on mobile */}
                    <h3 className="text-xl sm:text-2xl md:text-3xl font-bold text-white flex items-center gap-2 sm:gap-3"> {/* Adjusted font size and gap */}
                      <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r from-cyan-400 to-purple-400 rounded-xl flex items-center justify-center"> {/* Adjusted size */}
                        <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" /> {/* Adjusted size */}
                      </div>
                      Analysis Results
                    </h3>
                    
                    <div className="group relative">
                      <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-xl blur opacity-25 group-hover:opacity-75 transition duration-500"></div>
                      <Button
                        variant="outline"
                        onClick={() => setShowUrdu(!showUrdu)}
                        className="relative bg-gray-800/60 border-2 border-cyan-400/50 text-cyan-300 hover:bg-gray-700/80 hover:border-cyan-400 transition-all duration-300 backdrop-blur-lg font-bold px-4 py-2 text-sm sm:px-auto sm:py-auto sm:text-base" // Adjusted padding and font size
                      >
                        <Languages className="w-3 h-3 mr-1 sm:w-4 sm:h-4 sm:mr-2" /> {/* Adjusted icon size */}
                        {showUrdu ? 'ENGLISH' : 'اردو'}
                      </Button>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 md:p-8 space-y-6 sm:space-y-8 md:space-y-10"> {/* Adjusted padding and space */}
                  {/* Article Title */}
                  <div className="space-y-3 sm:space-y-4"> {/* Adjusted space */}
                    <h4 className="text-lg sm:text-xl font-bold text-white flex items-center gap-2 sm:gap-3"> {/* Adjusted font size and gap */}
                      <div className="w-7 h-7 sm:w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center"> {/* Adjusted size */}
                        <span className="text-white text-xs sm:text-sm">📰</span> {/* Adjusted font size */}
                      </div>
                      Article Title
                    </h4>
                    <div className="group relative">
                      <div className="absolute -inset-1 bg-gradient-to-r from-yellow-600/20 to-orange-600/20 rounded-2xl blur opacity-50"></div>
                      <div className="relative p-5 sm:p-6 bg-gradient-to-br from-gray-800/60 to-gray-700/60 rounded-2xl border border-gray-600/50 backdrop-blur-lg"> {/* Adjusted padding */}
                        <p className="text-white font-semibold text-base sm:text-xl leading-relaxed"> {/* Adjusted font size */}
                          {showUrdu ? (result.title_urdu || result.title) : result.title}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Smart Summary */}
                  <div className="space-y-3 sm:space-y-4"> {/* Adjusted space */}
                    <h4 className="text-lg sm:text-xl font-bold text-white flex items-center gap-2 sm:gap-3"> {/* Adjusted font size and gap */}
                      <div className="w-7 h-7 sm:w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center"> {/* Adjusted size */}
                        <Brain className="w-4 h-4 sm:w-5 h-5 text-white" /> {/* Adjusted size */}
                      </div>
                      Smart Summary
                      <div className="ml-1 sm:ml-2 px-3 py-1.5 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full text-xs text-purple-300 border border-purple-400/30 font-bold backdrop-blur-lg sm:px-4 sm:py-2 sm:text-sm"> {/* Adjusted padding and font size */}
                        {showUrdu ? 'اردو' : 'ENGLISH'}
                      </div>
                    </h4>
                    
                    <div className="group relative">
                      <div className="absolute -inset-1 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl blur opacity-50"></div>
                      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-gray-800/60 to-gray-700/60 border border-gray-600/50 backdrop-blur-lg">
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-pink-500/5"></div>
                        <div className="relative p-6 sm:p-8">
                          <div className="prose prose-sm sm:prose-lg max-w-none"> {/* Adjusted prose size for mobile */}
                            <p className="text-gray-200 leading-relaxed text-base sm:text-lg"> 
                              {showUrdu ? result.ai_summary_urdu : result.ai_summary}
                            </p>
                          </div>
                        </div>
                        
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 animate-pulse"></div>
                      </div>
                    </div>
                  </div>

                  {/* Metadata */}
                  {(result.author || result.publish_date || result.description) && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 pt-6 md:pt-8 border-t border-gray-700/50">
                      {result.author && (
                        <div className="group relative">
                          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600/20 to-cyan-600/20 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
                          <div className="relative space-y-2 p-4 bg-gray-800/40 rounded-xl border border-gray-600/30 backdrop-blur-lg">
                            <div className="flex items-center gap-2 text-xs font-bold text-blue-300 sm:text-sm"> {/* Adjusted font size */}
                              <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full sm:w-4 sm:h-4"></div> {/* Adjusted size */}
                              AUTHOR
                            </div>
                            <div className="text-blue-400 font-medium text-sm sm:text-base">{result.author}</div> {/* Adjusted font size */}
                          </div>
                        </div>
                      )}
                      {result.publish_date && (
                        <div className="group relative">
                          <div className="absolute -inset-1 bg-gradient-to-r from-green-600/20 to-emerald-600/20 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
                          <div className="relative space-y-2 p-4 bg-gray-800/40 rounded-xl border border-gray-600/30 backdrop-blur-lg">
                            <div className="flex items-center gap-2 text-xs font-bold text-green-300 sm:text-sm"> {/* Adjusted font size */}
                              <div className="w-3 h-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full sm:w-4 sm:h-4"></div> {/* Adjusted size */}
                              PUBLISHED
                            </div>
                            <div className="text-green-400 font-medium text-sm sm:text-base">{result.publish_date}</div> {/* Adjusted font size */}
                          </div>
                        </div>
                      )}
                      {result.description && (
                        <div className="group relative">
                          <div className="absolute -inset-1 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
                          <div className="relative space-y-2 p-4 bg-gray-800/40 rounded-xl border border-gray-600/30 backdrop-blur-lg">
                            <div className="flex items-center gap-2 text-xs font-bold text-purple-300 sm:text-sm"> {/* Adjusted font size */}
                              <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full sm:w-4 sm:h-4"></div> {/* Adjusted size */}
                              DESCRIPTION
                            </div>
                            <div className="text-purple-400 font-medium line-clamp-3 text-sm sm:text-base">{result.description}</div> {/* Adjusted font size */}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-2 sm:gap-3 md:gap-4 pt-6 md:pt-8 border-t border-gray-700/50"> {/* Adjusted gap and padding */}
                    {[
                      { 
                        label: `Switch to ${showUrdu ? 'English' : 'اردو'}`,
                        icon: <Languages className="w-3 h-3 sm:w-4 h-4" />, // Adjusted size
                        action: () => setShowUrdu(!showUrdu),
                        gradient: 'from-cyan-600 to-blue-600'
                      },
                      { 
                        label: 'Copy Summary',
                        icon: <span className="text-xs sm:text-sm">📋</span>, // Adjusted size
                        action: () => navigator.clipboard.writeText(showUrdu ? result.ai_summary_urdu : result.ai_summary),
                        gradient: 'from-purple-600 to-pink-600'
                      },
                      { 
                        label: 'View Source',
                        icon: <span className="text-xs sm:text-sm">🔗</span>, // Adjusted size
                        action: () => window.open(url, '_blank'),
                        gradient: 'from-green-600 to-emerald-600'
                      }
                    ].map((button, index) => (
                      <div key={index} className="group relative">
                        <div className={`absolute -inset-1 bg-gradient-to-r ${button.gradient} rounded-xl blur opacity-25 group-hover:opacity-75 transition duration-500`}></div>
                        <Button
                          variant="outline"
                          onClick={button.action}
                          className="relative bg-gray-800/60 border-2 border-gray-600/50 text-white hover:bg-gray-700/80 hover:border-cyan-400/50 transition-all duration-300 backdrop-blur-lg font-bold text-xs sm:text-sm px-3 py-1.5 sm:px-auto sm:py-auto" // Adjusted padding and font size
                        >
                          {button.icon}
                          <span className="ml-1 sm:ml-2">{button.label}</span> {/* Adjusted margin */}
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Custom Styles */}
        <style jsx>{`
          @keyframes slideInUp {
            from {
              opacity: 0;
              transform: translateY(20px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          @keyframes fadeInText {
            from {
              opacity: 0;
              transform: translateY(10px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }
          
          .line-clamp-3 {
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
          
          .prose {
            color: inherit;
          }
          
          .prose p {
            margin-bottom: 0;
          }
          
          .border-3 {
            border-width: 3px;
          }
        `}</style>
      </div>
    </div>
  );
}