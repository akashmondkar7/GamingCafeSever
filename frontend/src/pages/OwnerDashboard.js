import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { LayoutDashboard, Gamepad2, TrendingUp, Users, Bot, Settings, LogOut, Send, Sparkles } from 'lucide-react';

export const OwnerDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [analytics, setAnalytics] = useState(null);
  const [devices, setDevices] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [aiMessage, setAiMessage] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [showAiChat, setShowAiChat] = useState(false);

  useEffect(() => {
    fetchAnalytics();
    fetchDevices();
    fetchSessions();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const { data } = await api.get('/analytics/dashboard');
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchDevices = async () => {
    try {
      const { data } = await api.get('/devices');
      setDevices(data);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  const fetchSessions = async () => {
    try {
      const { data } = await api.get('/sessions');
      setSessions(data);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const handleAiChat = async () => {
    if (!aiMessage.trim()) return;
    
    setAiLoading(true);
    try {
      const { data } = await api.post('/ai/chat', {
        message: aiMessage,
        agent_type: 'OWNER_ASSISTANT'
      });
      setAiResponse(data.response);
      toast.success('AI response generated');
    } catch (error) {
      toast.error('Failed to get AI response');
      console.error(error);
    } finally {
      setAiLoading(false);
    }
  };

  const activeSessions = sessions.filter(s => s.status === 'ACTIVE');

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <div className="bg-surface border-b border-white/10 sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-heading font-bold text-primary">GAME CAFÉ</h1>
            <p className="text-xs text-zinc-400">Café Owner Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              data-testid="ai-chat-button"
              variant="outline"
              size="sm"
              className="border-primary/50 text-primary hover:bg-primary/10"
              onClick={() => setShowAiChat(!showAiChat)}
            >
              <Bot className="w-4 h-4 mr-2" />
              AI Assistant
            </Button>
            <div className="text-right">
              <p className="text-sm font-medium">{user?.name}</p>
              <p className="text-xs text-zinc-400">{user?.role}</p>
            </div>
            <Button
              data-testid="logout-button"
              variant="ghost"
              size="icon"
              onClick={logout}
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-surface border-r border-white/10 min-h-[calc(100vh-73px)]">
          <nav className="p-4 space-y-2">
            <button
              data-testid="nav-overview"
              onClick={() => setActiveTab('overview')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'overview' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>Overview</span>
            </button>
            <button
              data-testid="nav-devices"
              onClick={() => setActiveTab('devices')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'devices' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <Gamepad2 className="w-5 h-5" />
              <span>Devices</span>
            </button>
            <button
              data-testid="nav-sessions"
              onClick={() => setActiveTab('sessions')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'sessions' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <Users className="w-5 h-5" />
              <span>Sessions</span>
            </button>
            <button
              data-testid="nav-analytics"
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'analytics' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <TrendingUp className="w-5 h-5" />
              <span>Analytics</span>
            </button>
            <button
              data-testid="nav-settings"
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'settings' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <Settings className="w-5 h-5" />
              <span>Settings</span>
            </button>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {activeTab === 'overview' && (
            <div data-testid="overview-content">
              <h2 className="text-3xl font-heading font-bold mb-6">Dashboard Overview</h2>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Total Devices</p>
                  <p className="text-4xl font-heading font-bold" data-testid="stat-devices">{analytics?.total_devices || 0}</p>
                </Card>
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Active Sessions</p>
                  <p className="text-4xl font-heading font-bold text-accent-success" data-testid="stat-active-sessions">{analytics?.active_sessions || 0}</p>
                </Card>
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Today Revenue</p>
                  <p className="text-4xl font-heading font-bold text-primary" data-testid="stat-today-revenue">₹{analytics?.today_revenue || 0}</p>
                </Card>
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Utilization</p>
                  <p className="text-4xl font-heading font-bold text-secondary" data-testid="stat-utilization">{analytics?.avg_utilization || 0}%</p>
                </Card>
              </div>

              {/* AI Insights Widget */}
              <Card className="bg-gradient-to-br from-primary/10 to-surface border border-primary/30 p-6 mb-8">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-sm bg-primary/20 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-heading font-bold mb-2">AI Insights</h3>
                    <p className="text-zinc-300 mb-4">
                      Your café has {activeSessions.length} active sessions. Current utilization is {analytics?.avg_utilization || 0}%.
                      {(analytics?.avg_utilization || 0) < 50 && " Consider running promotions to increase utilization during off-peak hours."}
                    </p>
                    <Button
                      data-testid="ask-ai-button"
                      size="sm"
                      className="bg-primary hover:bg-primary-hover"
                      onClick={() => setShowAiChat(true)}
                    >
                      Ask AI for Recommendations
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Recent Sessions */}
              <Card className="bg-surface border-white/10 p-6">
                <h3 className="text-xl font-heading font-bold mb-4">Active Sessions</h3>
                <div className="space-y-3">
                  {activeSessions.length === 0 ? (
                    <p className="text-zinc-400 text-center py-8">No active sessions</p>
                  ) : (
                    activeSessions.slice(0, 5).map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-3 bg-background rounded-sm border border-white/5">
                        <div>
                          <p className="font-medium">Device: {session.device_id.slice(0, 8)}</p>
                          <p className="text-xs text-zinc-400">Started: {new Date(session.start_time).toLocaleTimeString()}</p>
                        </div>
                        <div className="px-3 py-1 bg-accent-success/20 text-accent-success rounded-sm text-xs font-mono">
                          ACTIVE
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'devices' && (
            <div data-testid="devices-content">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-heading font-bold">Device Management</h2>
                <Button data-testid="add-device-button" className="bg-primary hover:bg-primary-hover">+ Add Device</Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {devices.length === 0 ? (
                  <p className="text-zinc-400 col-span-3 text-center py-12">No devices yet. Add your first device.</p>
                ) : (
                  devices.map((device) => (
                    <Card key={device.id} className="bg-surface border-white/10 p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-heading font-bold text-lg">{device.name}</h3>
                          <p className="text-xs text-zinc-400 uppercase tracking-wider">{device.device_type}</p>
                        </div>
                        <div className={`px-2 py-1 rounded-sm text-xs font-mono ${
                          device.status === 'AVAILABLE' ? 'bg-accent-success/20 text-accent-success' :
                          device.status === 'OCCUPIED' ? 'bg-accent-warning/20 text-accent-warning' :
                          'bg-zinc-700 text-zinc-300'
                        }`}>
                          {device.status}
                        </div>
                      </div>
                      <div className="mb-4">
                        <p className="text-2xl font-heading font-bold text-primary">₹{device.hourly_rate}/hr</p>
                      </div>
                      {device.specifications && (
                        <p className="text-sm text-zinc-400">{device.specifications}</p>
                      )}
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'sessions' && (
            <div data-testid="sessions-content">
              <h2 className="text-3xl font-heading font-bold mb-6">Session History</h2>
              
              <Card className="bg-surface border-white/10 p-6">
                <div className="space-y-3">
                  {sessions.length === 0 ? (
                    <p className="text-zinc-400 text-center py-12">No sessions yet</p>
                  ) : (
                    sessions.slice(0, 20).map((session) => (
                      <div key={session.id} className="flex items-center justify-between p-4 bg-background rounded-sm border border-white/5">
                        <div className="flex-1">
                          <p className="font-medium font-mono">Session #{session.id.slice(0, 8)}</p>
                          <p className="text-sm text-zinc-400">
                            {new Date(session.start_time).toLocaleString()}
                            {session.duration_hours && ` • ${session.duration_hours.toFixed(2)}h`}
                          </p>
                        </div>
                        <div className="flex items-center gap-4">
                          {session.total_amount > 0 && (
                            <p className="text-lg font-heading font-bold text-primary">₹{session.total_amount.toFixed(2)}</p>
                          )}
                          <div className={`px-3 py-1 rounded-sm text-xs font-mono ${
                            session.status === 'ACTIVE' ? 'bg-accent-success/20 text-accent-success' :
                            session.status === 'COMPLETED' ? 'bg-zinc-700 text-zinc-300' :
                            'bg-accent-info/20 text-accent-info'
                          }`}>
                            {session.status}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div data-testid="analytics-content">
              <h2 className="text-3xl font-heading font-bold mb-6">Analytics & Reports</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-surface border-white/10 p-6">
                  <h3 className="text-xl font-heading font-bold mb-4">Revenue Metrics</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-zinc-400">Total Revenue</p>
                      <p className="text-3xl font-heading font-bold text-primary">₹{analytics?.total_revenue || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-zinc-400">Today's Revenue</p>
                      <p className="text-2xl font-heading font-bold text-secondary">₹{analytics?.today_revenue || 0}</p>
                    </div>
                  </div>
                </Card>

                <Card className="bg-surface border-white/10 p-6">
                  <h3 className="text-xl font-heading font-bold mb-4">Utilization</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-zinc-400">Average Utilization</p>
                      <p className="text-3xl font-heading font-bold text-accent-success">{analytics?.avg_utilization || 0}%</p>
                    </div>
                    <div className="w-full bg-zinc-800 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-primary to-secondary h-3 rounded-full transition-all"
                        style={{ width: `${analytics?.avg_utilization || 0}%` }}
                      ></div>
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div data-testid="settings-content">
              <h2 className="text-3xl font-heading font-bold mb-6">Settings</h2>
              <Card className="bg-surface border-white/10 p-6">
                <p className="text-zinc-400">Settings panel - Coming soon</p>
              </Card>
            </div>
          )}
        </div>
      </div>

      {/* AI Chat Sidebar */}
      {showAiChat && (
        <div className="fixed right-0 top-[73px] bottom-0 w-96 bg-surface border-l border-white/10 z-50" data-testid="ai-chat-panel">
          <div className="flex flex-col h-full">
            <div className="p-4 border-b border-white/10 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-primary" />
                <h3 className="font-heading font-bold">AI Assistant</h3>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setShowAiChat(false)}>
                ×
              </Button>
            </div>
            
            <ScrollArea className="flex-1 p-4">
              {aiResponse ? (
                <Card className="bg-primary/5 border-primary/30 p-4 mb-4">
                  <p className="text-xs text-zinc-400 mb-2">AI Response:</p>
                  <p className="text-sm text-zinc-200 whitespace-pre-wrap">{aiResponse}</p>
                </Card>
              ) : (
                <div className="text-center py-12 text-zinc-400">
                  <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Ask me anything about your café!</p>
                </div>
              )}
            </ScrollArea>
            
            <div className="p-4 border-t border-white/10">
              <Textarea
                data-testid="ai-input"
                placeholder="Ask about revenue, utilization, suggestions..."
                value={aiMessage}
                onChange={(e) => setAiMessage(e.target.value)}
                className="mb-2 bg-background border-white/10 min-h-[80px]"
              />
              <Button
                data-testid="send-ai-message"
                className="w-full bg-primary hover:bg-primary-hover"
                onClick={handleAiChat}
                disabled={aiLoading || !aiMessage.trim()}
              >
                {aiLoading ? 'Thinking...' : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Send Message
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
