const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async scrapeBlog(url: string) {
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

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error scraping blog:', error);
      throw error;
    }
  },

  async checkHealth() {
    try {
      console.log(`🏥 Checking API health: ${API_BASE_URL}/health`);
      
      const response = await fetch(`${API_BASE_URL}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error checking health:', error);
      throw error;
    }
  },

  async getRecentSummaries(limit: number = 10) {
    try {
      console.log(`📋 Getting recent summaries: ${API_BASE_URL}/recent?limit=${limit}`);
      
      const response = await fetch(`${API_BASE_URL}/recent?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error getting recent summaries:', error);
      throw error;
    }
  },

  getApiUrl(): string {
    return API_BASE_URL;
  }
};

// Export individual functions for convenience
export const { scrapeBlog, checkHealth, getRecentSummaries, getApiUrl } = api;