import React, { useState, useEffect } from 'react';
import { apiService } from './ApiService';

const AdvancedFeatures = () => {
  const [automationStatus, setAutomationStatus] = useState({
    is_running: false,
    auto_reply_enabled: true,
    follow_up_enabled: true,
    lead_scoring_enabled: true
  });
  const [analytics, setAnalytics] = useState({});
  const [aiPerformance, setAiPerformance] = useState({});
  const [bulkMessage, setBulkMessage] = useState('');
  const [targetTags, setTargetTags] = useState(['warm_lead', 'hot_lead']);
  const [testMessage, setTestMessage] = useState('');
  const [smartReply, setSmartReply] = useState('');

  useEffect(() => {
    fetchAutomationStatus();
    fetchAnalytics();
    fetchAiPerformance();
  }, []);

  const fetchAutomationStatus = async () => {
    try {
      const response = await fetch(`${apiService.baseURL}/automation/status`);
      const data = await response.json();
      setAutomationStatus(data);
      setAnalytics(data.analytics || {});
    } catch (error) {
      console.error('Error fetching automation status:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${apiService.baseURL}/analytics/automation`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchAiPerformance = async () => {
    try {
      const response = await fetch(`${apiService.baseURL}/analytics/ai-performance`);
      const data = await response.json();
      setAiPerformance(data);
    } catch (error) {
      console.error('Error fetching AI performance:', error);
    }
  };

  const toggleAutomation = async (action) => {
    try {
      const response = await fetch(`${apiService.baseURL}/automation/${action}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        fetchAutomationStatus();
      }
    } catch (error) {
      console.error(`Error ${action} automation:`, error);
    }
  };

  const updateAutomationSettings = async (settings) => {
    try {
      const response = await fetch(`${apiService.baseURL}/automation/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      const data = await response.json();
      if (data.success) {
        fetchAutomationStatus();
      }
    } catch (error) {
      console.error('Error updating automation settings:', error);
    }
  };

  const testSmartReply = async () => {
    try {
      const response = await fetch(`${apiService.baseURL}/ai/smart-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: testMessage })
      });
      const data = await response.json();
      setSmartReply(data.reply || 'No reply generated');
    } catch (error) {
      console.error('Error testing smart reply:', error);
    }
  };

  const sendBulkMessage = async () => {
    try {
      const response = await fetch(`${apiService.baseURL}/bulk/send-message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: bulkMessage,
          target_tags: targetTags,
          limit: 50
        })
      });
      const data = await response.json();
      alert(`Bulk message sent to ${data.sent_count} doctors`);
      setBulkMessage('');
    } catch (error) {
      console.error('Error sending bulk message:', error);
    }
  };

  const manualTrigger = async (action) => {
    try {
      const response = await fetch(`${apiService.baseURL}/manual/${action}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert(data.message);
        fetchAnalytics();
      }
    } catch (error) {
      console.error(`Error triggering ${action}:`, error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Automation Control */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">🤖 Automation Engine</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="font-medium">Engine Status:</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                automationStatus.is_running 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {automationStatus.is_running ? 'Active' : 'Inactive'}
              </span>
            </div>
            
            <div className="space-y-2">
              <button
                onClick={() => toggleAutomation('start')}
                disabled={automationStatus.is_running}
                className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                Start Automation
              </button>
              <button
                onClick={() => toggleAutomation('stop')}
                disabled={!automationStatus.is_running}
                className="w-full bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
              >
                Stop Automation
              </button>
            </div>
          </div>
          
          <div>
            <h3 className="font-medium mb-3">Automation Settings</h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={automationStatus.auto_reply_enabled}
                  onChange={(e) => updateAutomationSettings({ auto_reply_enabled: e.target.checked })}
                  className="mr-2"
                />
                Auto Reply
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={automationStatus.follow_up_enabled}
                  onChange={(e) => updateAutomationSettings({ follow_up_enabled: e.target.checked })}
                  className="mr-2"
                />
                Follow-up Messages
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={automationStatus.lead_scoring_enabled}
                  onChange={(e) => updateAutomationSettings({ lead_scoring_enabled: e.target.checked })}
                  className="mr-2"
                />
                Lead Scoring
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Dashboard */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📊 Automation Analytics</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{analytics.messages_today || 0}</div>
            <div className="text-sm text-gray-600">Messages Today</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{analytics.ai_messages_today || 0}</div>
            <div className="text-sm text-gray-600">AI Messages</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{analytics.automation_rate || 0}%</div>
            <div className="text-sm text-gray-600">Automation Rate</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {analytics.lead_distribution ? Object.values(analytics.lead_distribution).reduce((a, b) => a + b, 0) : 0}
            </div>
            <div className="text-sm text-gray-600">Total Leads</div>
          </div>
        </div>

        {/* Lead Distribution */}
        {analytics.lead_distribution && (
          <div>
            <h3 className="font-medium mb-3">Lead Distribution</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div className="bg-red-100 p-3 rounded text-center">
                <div className="font-bold text-red-600">{analytics.lead_distribution.hot_lead}</div>
                <div className="text-xs">Hot Leads</div>
              </div>
              <div className="bg-yellow-100 p-3 rounded text-center">
                <div className="font-bold text-yellow-600">{analytics.lead_distribution.warm_lead}</div>
                <div className="text-xs">Warm Leads</div>
              </div>
              <div className="bg-blue-100 p-3 rounded text-center">
                <div className="font-bold text-blue-600">{analytics.lead_distribution.cold_lead}</div>
                <div className="text-xs">Cold Leads</div>
              </div>
              <div className="bg-green-100 p-3 rounded text-center">
                <div className="font-bold text-green-600">{analytics.lead_distribution.registered}</div>
                <div className="text-xs">Registered</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Performance */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">🧠 AI Agent Performance</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(aiPerformance).map(([key, agent]) => (
            <div key={key} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium">{agent.name}</h3>
                <span className={`px-2 py-1 rounded text-xs ${
                  agent.status === 'active' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {agent.status}
                </span>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <div>Accuracy: {agent.accuracy || agent.performance || 0}%</div>
                <div>
                  {agent.responses_today && `Responses: ${agent.responses_today}`}
                  {agent.scores_updated_today && `Scores Updated: ${agent.scores_updated_today}`}
                  {agent.follow_ups_sent_today && `Follow-ups: ${agent.follow_ups_sent_today}`}
                  {agent.queries_processed_today && `Queries: ${agent.queries_processed_today}`}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Smart Reply Tester */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">🎯 Smart Reply Tester</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Test Message:</label>
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Enter a message to test smart reply..."
              className="w-full border rounded-lg px-3 py-2"
            />
          </div>
          <button
            onClick={testSmartReply}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Generate Smart Reply
          </button>
          {smartReply && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <strong>AI Reply:</strong> {smartReply}
            </div>
          )}
        </div>
      </div>

      {/* Bulk Messaging */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">📢 Bulk Messaging</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Message:</label>
            <textarea
              value={bulkMessage}
              onChange={(e) => setBulkMessage(e.target.value)}
              placeholder="Enter your bulk message..."
              rows={3}
              className="w-full border rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Target Tags:</label>
            <div className="flex flex-wrap gap-2">
              {['hot_lead', 'warm_lead', 'cold_lead', 'registered'].map(tag => (
                <label key={tag} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={targetTags.includes(tag)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setTargetTags([...targetTags, tag]);
                      } else {
                        setTargetTags(targetTags.filter(t => t !== tag));
                      }
                    }}
                    className="mr-1"
                  />
                  <span className="text-sm">{tag.replace('_', ' ')}</span>
                </label>
              ))}
            </div>
          </div>
          <button
            onClick={sendBulkMessage}
            disabled={!bulkMessage.trim()}
            className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
          >
            Send Bulk Message
          </button>
        </div>
      </div>

      {/* Manual Triggers */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">⚡ Manual Triggers</h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            onClick={() => manualTrigger('process-auto-replies')}
            className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm"
          >
            Process Auto Replies
          </button>
          <button
            onClick={() => manualTrigger('update-lead-scores')}
            className="bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 text-sm"
          >
            Update Lead Scores
          </button>
          <button
            onClick={() => manualTrigger('send-follow-ups')}
            className="bg-pink-600 text-white px-4 py-2 rounded hover:bg-pink-700 text-sm"
          >
            Send Follow-ups
          </button>
          <button
            onClick={() => manualTrigger('health-check')}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm"
          >
            Health Check
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFeatures;

