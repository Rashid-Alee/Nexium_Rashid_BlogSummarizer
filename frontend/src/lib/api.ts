class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = this.getApiUrl();
  }

  getApiUrl(): string {
    if (typeof window !== 'undefined') {
      return process.env.NEXT_PUBLIC_API_URL || 'https://blog-scraper-api.onrender.com';
    } else {
      return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://blog-scraper-api.onrender.com';
    }
  }

  async checkHealth(): Promise<any> {
    try {
      console.log(`🏥 Checking API health: ${this.baseUrl}/health`);
      
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Health check failed:', error);
      throw error;
    }
  }

  async scrapeBlog(url: string): Promise<any> {
    try {
      console.log(`🚀 Starting blog scrape for: ${url}`);
      
      const response = await fetch(`${this.baseUrl}/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Scrape failed:', error);
      throw error;
    }
  }

  async getRecentSummaries(limit: number = 10): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/recent?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Failed to get recent summaries:', error);
      throw error;
    }
  }

  async getStatistics(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Failed to get statistics:', error);
      throw error;
    }
  }
}

export const api = new ApiClient();