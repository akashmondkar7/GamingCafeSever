import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { LayoutDashboard, Building2, Users, TrendingUp, Settings, LogOut, DollarSign, Gamepad2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

export const SuperAdminDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [analytics, setAnalytics] = useState(null);
  const [cafes, setCafes] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);

  useEffect(() => {
    fetchAnalytics();
    fetchCafes();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const { data } = await api.get('/analytics/dashboard');
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchCafes = async () => {
    try {
      const { data } = await api.get('/cafes');
      setCafes(data);
    } catch (error) {
      console.error('Failed to fetch cafes:', error);
    }
  };

  const COLORS = ['#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <div className="bg-surface border-b border-white/10 sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-heading font-bold text-primary">GAME CAFÉ OS</h1>
            <p className="text-xs text-zinc-400">Super Admin Dashboard</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium">{user?.name}</p>
              <p className="text-xs text-zinc-400">SUPER ADMIN</p>
            </div>
            <Button variant="ghost" size="icon" onClick={logout}>
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
              onClick={() => setActiveTab('overview')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'overview' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>Overview</span>
            </button>
            <button
              onClick={() => setActiveTab('cafes')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'cafes' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <Building2 className="w-5 h-5" />
              <span>Cafés</span>
            </button>
            <button
              onClick={() => setActiveTab('revenue')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'revenue' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <DollarSign className="w-5 h-5" />
              <span>Revenue</span>
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-sm transition-colors ${
                activeTab === 'analytics' ? 'bg-primary text-white' : 'text-zinc-400 hover:bg-white/5'
              }`}
            >
              <TrendingUp className="w-5 h-5" />
              <span>Analytics</span>
            </button>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-3xl font-heading font-bold mb-6">Platform Overview</h2>
              
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <Card className="bg-gradient-to-br from-primary/10 to-surface border-primary/30 p-6">
                  <Building2 className="w-8 h-8 text-primary mb-3" />
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Total Cafés</p>
                  <p className="text-4xl font-heading font-bold">{analytics?.total_cafes || 0}</p>
                </Card>
                <Card className="bg-gradient-to-br from-secondary/10 to-surface border-secondary/30 p-6">
                  <Gamepad2 className="w-8 h-8 text-secondary mb-3" />
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Total Devices</p>
                  <p className="text-4xl font-heading font-bold">{analytics?.total_devices || 0}</p>
                </Card>
                <Card className="bg-gradient-to-br from-accent-success/10 to-surface border-accent-success/30 p-6">
                  <Users className="w-8 h-8 text-accent-success mb-3" />
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Active Sessions</p>
                  <p className="text-4xl font-heading font-bold">{analytics?.active_sessions || 0}</p>
                </Card>
                <Card className="bg-gradient-to-br from-accent-warning/10 to-surface border-accent-warning/30 p-6">
                  <DollarSign className="w-8 h-8 text-accent-warning mb-3" />
                  <p className="text-xs text-zinc-400 uppercase tracking-wider mb-2">Platform Revenue</p>
                  <p className="text-4xl font-heading font-bold">₹{analytics?.total_revenue || 0}</p>
                </Card>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <Card className="bg-surface border-white/10 p-6">
                  <h3 className="text-xl font-heading font-bold mb-4">Revenue Trend</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={[
                      { month: 'Jan', revenue: 50000 },
                      { month: 'Feb', revenue: 65000 },
                      { month: 'Mar', revenue: 75000 },
                      { month: 'Apr', revenue: 85000 },
                      { month: 'May', revenue: 95000 },
                      { month: 'Jun', revenue: 110000 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="month" stroke="#a1a1aa" />
                      <YAxis stroke="#a1a1aa" />
                      <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid rgba(255,255,255,0.1)' }} />
                      <Line type="monotone" dataKey="revenue" stroke="#7c3aed" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>

                <Card className="bg-surface border-white/10 p-6">
                  <h3 className="text-xl font-heading font-bold mb-4">Café Distribution</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={[
                      { city: 'Mumbai', count: 25 },
                      { city: 'Delhi', count: 20 },
                      { city: 'Bangalore', count: 30 },
                      { city: 'Hyderabad', count: 15 },
                      { city: 'Pune', count: 18 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="city" stroke="#a1a1aa" />
                      <YAxis stroke="#a1a1aa" />
                      <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid rgba(255,255,255,0.1)' }} />
                      <Bar dataKey="count" fill="#06b6d4" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </div>
            </div>
          )}

          {activeTab === 'cafes' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-heading font-bold">All Cafés</h2>
              </div>
              
              <div className="grid grid-cols-1 gap-4">
                {cafes.length === 0 ? (
                  <p className="text-zinc-400 text-center py-12">No cafés registered yet</p>
                ) : (
                  cafes.map(cafe => (
                    <Card key={cafe.id} className="bg-surface border-white/10 p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-xl font-heading font-bold mb-2">{cafe.name}</h3>
                          <p className="text-sm text-zinc-400 mb-1">{cafe.address}, {cafe.city}</p>
                          <p className="text-xs text-zinc-500">Owner ID: {cafe.owner_id}</p>
                        </div>
                        <div className={`px-3 py-1 rounded-sm text-xs font-mono ${
                          cafe.is_active ? 'bg-accent-success/20 text-accent-success' : 'bg-zinc-700 text-zinc-400'
                        }`}>
                          {cafe.is_active ? 'ACTIVE' : 'INACTIVE'}
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'revenue' && (
            <div>
              <h2 className="text-3xl font-heading font-bold mb-6">Revenue Analytics</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-sm text-zinc-400 mb-2">Today's Revenue</p>
                  <p className="text-3xl font-heading font-bold text-primary">₹{analytics?.today_revenue || 0}</p>
                </Card>
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-sm text-zinc-400 mb-2">Total Platform Revenue</p>
                  <p className="text-3xl font-heading font-bold text-secondary">₹{analytics?.total_revenue || 0}</p>
                </Card>
                <Card className="bg-surface border-white/10 p-6">
                  <p className="text-sm text-zinc-400 mb-2">Average Revenue/Café</p>
                  <p className="text-3xl font-heading font-bold text-accent-success">
                    ₹{analytics?.total_cafes ? Math.round(analytics.total_revenue / analytics.total_cafes) : 0}
                  </p>
                </Card>
              </div>

              <Card className="bg-surface border-white/10 p-6">
                <h3 className="text-xl font-heading font-bold mb-4">Monthly Revenue Breakdown</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={[
                    { month: 'Jan', subscription: 30000, session: 20000 },
                    { month: 'Feb', subscription: 35000, session: 30000 },
                    { month: 'Mar', subscription: 40000, session: 35000 },
                    { month: 'Apr', subscription: 45000, session: 40000 },
                    { month: 'May', subscription: 50000, session: 45000 },
                    { month: 'Jun', subscription: 55000, session: 55000 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#a1a1aa" />
                    <YAxis stroke="#a1a1aa" />
                    <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid rgba(255,255,255,0.1)' }} />
                    <Bar dataKey="subscription" fill="#7c3aed" name="Subscriptions" />
                    <Bar dataKey="session" fill="#06b6d4" name="Sessions" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div>
              <h2 className="text-3xl font-heading font-bold mb-6">Advanced Analytics</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-surface border-white/10 p-6">
                  <h3 className="text-xl font-heading font-bold mb-4">Device Utilization</h3>
                  <div className="text-center">
                    <p className="text-6xl font-heading font-bold text-primary mb-2">
                      {analytics?.avg_utilization || 0}%
                    </p>
                    <p className="text-sm text-zinc-400">Average Platform Utilization</p>
                  </div>
                  <div className="mt-6 w-full bg-zinc-800 rounded-full h-4">
                    <div
                      className="bg-gradient-to-r from-primary to-secondary h-4 rounded-full transition-all"
                      style={{ width: `${analytics?.avg_utilization || 0}%` }}
                    ></div>
                  </div>
                </Card>

                <Card className="bg-surface border-white/10 p-6">
                  <h3 className="text-xl font-heading font-bold mb-4">Platform Growth</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={[
                      { month: 'Jan', cafes: 10, devices: 50 },
                      { month: 'Feb', cafes: 15, devices: 80 },
                      { month: 'Mar', cafes: 22, devices: 120 },
                      { month: 'Apr', cafes: 30, devices: 160 },
                      { month: 'May', cafes: 40, devices: 210 },
                      { month: 'Jun', cafes: 50, devices: 270 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="month" stroke="#a1a1aa" />
                      <YAxis stroke="#a1a1aa" />
                      <Tooltip contentStyle={{ backgroundColor: '#18181b', border: '1px solid rgba(255,255,255,0.1)' }} />
                      <Line type="monotone" dataKey="cafes" stroke="#7c3aed" name="Cafés" />
                      <Line type="monotone" dataKey="devices" stroke="#06b6d4" name="Devices" />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
