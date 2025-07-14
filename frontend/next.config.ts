import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Environment variables that will be available in the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://blog-scraper-api.onrender.com',
  },
  
  // API rewrites for better development experience
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://blog-scraper-api.onrender.com'}/:path*`,
      },
    ]
  },
  
  // Security headers for production
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ]
  },
  
  // Optimize for production
  poweredByHeader: false,
  generateEtags: false,
  
  // DISABLE ESLINT FOR PRODUCTION BUILD
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // DISABLE TYPESCRIPT ERRORS FOR PRODUCTION BUILD
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Enable experimental features if needed
  experimental: {
    // Add any experimental features you need
  },
}

export default nextConfig