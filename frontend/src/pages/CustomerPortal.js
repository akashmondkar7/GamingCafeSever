import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Gamepad2, Clock, History, Wallet, LogOut } from 'lucide-react';

export const CustomerPortal = () => {
  const { user, logout } = useAuth();
  const [cafes, setCafes] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selectedCafe, setSelectedCafe] = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);

  useEffect(() => {
    fetchCafes();
    fetchMySessions();
  }, []);

  useEffect(() => {
    if (selectedCafe) {
      fetchDevices(selectedCafe.id);
    }
  }, [selectedCafe]);

  const fetchCafes = async () => {
    try {
      const { data } = await api.get('/cafes/public');
      setCafes(data);
    } catch (error) {
      console.error('Failed to fetch cafes:', error);
    }
  };

  const fetchMySessions = async () => {
    try {
      const { data } = await api.get('/sessions');
      setSessions(data);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const fetchDevices = async (cafeId) => {
    try {
      const { data } = await api.get(`/devices?cafe_id=${cafeId}`);
      setDevices(data);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  const handleBookDevice = async (device) => {
    try {
      await api.post('/sessions', {
        device_id: device.id,
        customer_id: user.id
      });
      toast.success('Session started successfully!');
      fetchMySessions();
      fetchDevices(selectedCafe.id);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start session');
    }
  };

  const activeSessions = sessions.filter(s => s.status === 'ACTIVE');
  const completedSessions = sessions.filter(s => s.status === 'COMPLETED');

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <div className="bg-surface border-b border-white/10 sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-heading font-bold text-primary">GAME CAFÉ</h1>
            <p className="text-xs text-zinc-400">Customer Portal</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-sm border border-primary/30">
              <Wallet className="w-4 h-4 text-primary" />
              <span className="font-mono font-bold">₹{user?.wallet_balance || 0}</span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium">{user?.name}</p>
              <p className="text-xs text-zinc-400">{user?.phone}</p>
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Active Sessions */}
        {activeSessions.length > 0 && (
          <Card className="bg-gradient-to-r from-accent-success/10 to-surface border border-accent-success/30 p-6 mb-8" data-testid="active-sessions">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-sm bg-accent-success/20 flex items-center justify-center">
                <Clock className="w-6 h-6 text-accent-success" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-heading font-bold mb-2">Active Gaming Session</h3>
                {activeSessions.map(session => (
                  <div key={session.id} className="flex items-center justify-between">
                    <p className="text-zinc-300">
                      Started: {new Date(session.start_time).toLocaleTimeString()}
                    </p>
                    <div className="px-3 py-1 bg-accent-success/20 text-accent-success rounded-sm text-xs font-mono">
                      ACTIVE
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Browse Cafes */}
        <div className="mb-8">
          <h2 className="text-3xl font-heading font-bold mb-6">Browse Gaming Cafés</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {cafes.map((cafe) => (
              <Card
                key={cafe.id}
                data-testid={`cafe-card-${cafe.slug}`}
                className={`bg-surface border-white/10 p-6 cursor-pointer transition-all hover:border-primary/50 ${
                  selectedCafe?.id === cafe.id ? 'border-primary shadow-glow' : ''
                }`}
                onClick={() => setSelectedCafe(cafe)}
              >
                <h3 className="font-heading font-bold text-xl mb-2">{cafe.name}</h3>
                <p className="text-sm text-zinc-400 mb-1">{cafe.address}</p>
                <p className="text-sm text-zinc-400">{cafe.city}</p>
                {cafe.description && (
                  <p className="text-sm text-zinc-300 mt-3">{cafe.description}</p>
                )}
              </Card>
            ))}
          </div>
        </div>

        {/* Available Devices */}
        {selectedCafe && (
          <div className="mb-8">
            <h2 className="text-3xl font-heading font-bold mb-6">
              Available Devices at {selectedCafe.name}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {devices.filter(d => d.status === 'AVAILABLE').length === 0 ? (
                <p className="text-zinc-400 col-span-4 text-center py-12">No devices available at the moment</p>
              ) : (
                devices
                  .filter(d => d.status === 'AVAILABLE')
                  .map((device) => (
                    <Card
                      key={device.id}
                      data-testid={`device-card-${device.id}`}
                      className="bg-surface border-white/10 p-6"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-heading font-bold">{device.name}</h3>
                          <p className="text-xs text-zinc-400 uppercase tracking-wider">{device.device_type}</p>
                        </div>
                        <div className="px-2 py-1 bg-accent-success/20 text-accent-success rounded-sm text-xs font-mono">
                          AVAILABLE
                        </div>
                      </div>
                      <div className="mb-4">
                        <p className="text-2xl font-heading font-bold text-primary">₹{device.hourly_rate}/hr</p>
                      </div>
                      <Button
                        data-testid={`book-device-${device.id}`}
                        className="w-full bg-primary hover:bg-primary-hover"
                        onClick={() => handleBookDevice(device)}
                      >
                        <Gamepad2 className="w-4 h-4 mr-2" />
                        Book Now
                      </Button>
                    </Card>
                  ))
              )}
            </div>
          </div>
        )}

        {/* Session History */}
        <div>
          <h2 className="text-3xl font-heading font-bold mb-6 flex items-center gap-2">
            <History className="w-8 h-8" />
            Session History
          </h2>
          <Card className="bg-surface border-white/10 p-6">
            <div className="space-y-3">
              {completedSessions.length === 0 ? (
                <p className="text-zinc-400 text-center py-12">No completed sessions yet</p>
              ) : (
                completedSessions.slice(0, 10).map((session) => (
                  <div
                    key={session.id}
                    data-testid={`session-${session.id}`}
                    className="flex items-center justify-between p-4 bg-background rounded-sm border border-white/5"
                  >
                    <div className="flex-1">
                      <p className="font-medium font-mono">Session #{session.id.slice(0, 8)}</p>
                      <p className="text-sm text-zinc-400">
                        {new Date(session.start_time).toLocaleString()}
                        {session.duration_hours && ` • ${session.duration_hours.toFixed(2)}h`}
                      </p>
                    </div>
                    <div className="text-right">
                      {session.total_amount > 0 && (
                        <p className="text-lg font-heading font-bold text-primary">₹{session.total_amount.toFixed(2)}</p>
                      )}
                      <p className="text-xs text-zinc-400">COMPLETED</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
