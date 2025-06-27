const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  static async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Dashboard Stats
  static async getDashboardStats() {
    return this.request('/dashboard/stats');
  }

  // WhatsApp Numbers
  static async getWhatsAppNumbers() {
    return this.request('/numbers');
  }

  static async addWhatsAppNumber(numberData) {
    return this.request('/numbers', {
      method: 'POST',
      body: JSON.stringify(numberData),
    });
  }

  // Doctors/Leads
  static async getDoctors() {
    return this.request('/doctors');
  }

  static async addDoctor(doctorData) {
    return this.request('/doctors', {
      method: 'POST',
      body: JSON.stringify(doctorData),
    });
  }

  // Chat Messages
  static async getChatMessages(doctorId) {
    return this.request(`/chat/${doctorId}/messages`);
  }

  static async sendMessage(doctorId, message) {
    return this.request(`/chat/${doctorId}/send`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // AI Agents
  static async getAIAgents() {
    return this.request('/agents');
  }

  static async restartAgent(agentId) {
    return this.request(`/agents/${agentId}/restart`, {
      method: 'POST',
    });
  }

  // Analytics
  static async getMessageAnalytics() {
    return this.request('/analytics/messages');
  }

  static async getLeadAnalytics() {
    return this.request('/analytics/leads');
  }

  // Initialize sample data
  static async initSampleData() {
    return this.request('/init-sample-data', {
      method: 'POST',
    });
  }
}

export default ApiService;

