const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Interfaces for type safety
interface ScrapeBlogRequest {
  url: string;
}

interface ScrapeBlogResponse {
  success: boolean;
  cached?: boolean;
  data?: any;
  error?: string;
  performance?: {
    total_time_ms?: number;
    response_time_ms?: number;
  };
  database?: {
    overall_success?: boolean;
    supabase?: { success: boolean };
    mongodb?: { success: boolean };
  };
}

interface HealthResponse {
  status: string;
  service: string;
  environment: string;
  databases: {
    supabase: any;
    mongodb: any;
    overall_status: string;
  };
  response_time_ms: number;
  version: string;
}

interface RecentSummariesResponse {
  success: boolean;
  data?: {
    summaries: any[];
    count: number;
    limit: number;
  };
  error?: string;
}

// Main API functions
export const api = {
  // Scrape blog function
  async scrapeBlog(url: string): Promise<ScrapeBlogResponse> {
    try {
      console.log(`🚀 Calling API: ${API_BASE_URL}/scrape`);
      
      const response = await fetch(`${API_BASE_URL}/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ScrapeBlogResponse = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error scraping blog:', error);
      throw error;
    }
  },

  // Health check function
  async checkHealth(): Promise<HealthResponse> {
    try {
      console.log(`🏥 Checking API health: ${API_BASE_URL}/health`);
      
      const response = await fetch(`${API_BASE_URL}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: HealthResponse = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error checking health:', error);
      throw error;
    }
  },

  // Get recent summaries function
  async getRecentSummaries(limit: number = 10): Promise<RecentSummariesResponse> {
    try {
      console.log(`📋 Getting recent summaries: ${API_BASE_URL}/recent?limit=${limit}`);
      
      const response = await fetch(`${API_BASE_URL}/recent?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: RecentSummariesResponse = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error getting recent summaries:', error);
      throw error;
    }
  },

  // Get API status (for debugging)
  getApiUrl(): string {
    return API_BASE_URL;
  }
};

// Export individual functions for convenience
export const { scrapeBlog, checkHealth, getRecentSummaries, getApiUrl } = api;