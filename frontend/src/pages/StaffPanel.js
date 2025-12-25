import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Clock, UserCheck, Gamepad2, CreditCard, LogOut, PlayCircle, StopCircle } from 'lucide-react';

export const StaffPanel = () => {
  const { user, logout } = useAuth();
  const [activeShift, setActiveShift] = useState(null);
  const [devices, setDevices] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [paymentAmount, setPaymentAmount] = useState('');

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      const { data } = await api.get('/devices');
      setDevices(data);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  const handleStartShift = async () => {
    try {
      const { data } = await api.post('/staff/shift/start');
      setActiveShift(data);
      toast.success('Shift started');
    } catch (error) {
      toast.error('Failed to start shift');
    }
  };

  const handleEndShift = async () => {
    if (!activeShift) return;
    try {
      await api.post(`/staff/shift/end/${activeShift.id}`);
      setActiveShift(null);
      toast.success('Shift ended');
    } catch (error) {
      toast.error('Failed to end shift');
    }
  };

  const handleCheckIn = async () => {
    if (!selectedDevice || !customerPhone) {
      toast.error('Please select device and enter customer phone');
      return;
    }

    try {
      // Find or create customer
      let customer;
      try {
        const { data } = await api.post('/auth/login', { phone: customerPhone });
        // Verify with mock OTP
        const verifyResponse = await api.post('/auth/verify-otp', { 
          phone: customerPhone, 
          otp: '123456' 
        });
        customer = verifyResponse.data.user;
      } catch (err) {
        // Register new customer
        const { data } = await api.post('/auth/register', {
          phone: customerPhone,
          name: `Customer ${customerPhone.slice(-4)}`,
          role: 'CUSTOMER'
        });
        customer = data.user;
      }

      // Create session
      await api.post('/sessions', {
        device_id: selectedDevice,
        customer_id: customer.id
      });

      toast.success('Customer checked in successfully');
      setSelectedDevice('');
      setCustomerPhone('');
      fetchDevices();
    } catch (error) {
      toast.error('Check-in failed');
      console.error(error);
    }
  };

  const handleCashPayment = async () => {
    if (!paymentAmount || parseFloat(paymentAmount) <= 0) {
      toast.error('Enter valid amount');
      return;
    }

    try {
      // Record cash payment
      toast.success(`Cash payment of ₹${paymentAmount} recorded`);
      setPaymentAmount('');
    } catch (error) {
      toast.error('Payment recording failed');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <div className="bg-surface border-b border-white/10 sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-heading font-bold text-primary">GAME CAFÉ</h1>
            <p className="text-xs text-zinc-400">Staff Panel</p>
          </div>
          <div className="flex items-center gap-4">
            {!activeShift ? (
              <Button
                data-testid="start-shift-button"
                onClick={handleStartShift}
                className="bg-accent-success hover:bg-accent-success/80"
              >
                <PlayCircle className="w-4 h-4 mr-2" />
                Start Shift
              </Button>
            ) : (
              <Button
                data-testid="end-shift-button"
                onClick={handleEndShift}
                variant="destructive"
              >
                <StopCircle className="w-4 h-4 mr-2" />
                End Shift
              </Button>
            )}
            <div className="text-right">
              <p className="text-sm font-medium">{user?.name}</p>
              <p className="text-xs text-zinc-400">{user?.role}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={logout}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Customer Check-in */}
          <Card className="bg-surface border-white/10 p-6" data-testid="checkin-card">
            <div className="flex items-center gap-3 mb-6">
              <UserCheck className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-heading font-bold">Customer Check-in</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Customer Phone</label>
                <Input
                  data-testid="customer-phone-input"
                  type="tel"
                  placeholder="Enter phone number"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value)}
                  className="bg-background border-white/10"
                />
              </div>

              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Select Device</label>
                <Select value={selectedDevice} onValueChange={setSelectedDevice}>
                  <SelectTrigger data-testid="device-select" className="bg-background border-white/10">
                    <SelectValue placeholder="Choose device" />
                  </SelectTrigger>
                  <SelectContent>
                    {devices.filter(d => d.status === 'AVAILABLE').map(device => (
                      <SelectItem key={device.id} value={device.id}>
                        {device.name} ({device.device_type}) - ₹{device.hourly_rate}/hr
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                data-testid="checkin-button"
                onClick={handleCheckIn}
                className="w-full bg-primary hover:bg-primary-hover"
                disabled={!activeShift}
              >
                <UserCheck className="w-4 h-4 mr-2" />
                Check In Customer
              </Button>
            </div>
          </Card>

          {/* Cash Payment */}
          <Card className="bg-surface border-white/10 p-6" data-testid="payment-card">
            <div className="flex items-center gap-3 mb-6">
              <CreditCard className="w-6 h-6 text-secondary" />
              <h2 className="text-2xl font-heading font-bold">Cash Payment</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-zinc-400 mb-2 block">Amount (₹)</label>
                <Input
                  data-testid="payment-amount-input"
                  type="number"
                  placeholder="Enter amount"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  className="bg-background border-white/10"
                />
              </div>

              <Button
                data-testid="record-payment-button"
                onClick={handleCashPayment}
                className="w-full bg-secondary hover:bg-secondary/80"
                disabled={!activeShift}
              >
                <CreditCard className="w-4 h-4 mr-2" />
                Record Payment
              </Button>
            </div>
          </Card>

          {/* Available Devices */}
          <Card className="bg-surface border-white/10 p-6 md:col-span-2" data-testid="devices-card">
            <div className="flex items-center gap-3 mb-6">
              <Gamepad2 className="w-6 h-6 text-accent-success" />
              <h2 className="text-2xl font-heading font-bold">Device Status</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {devices.length === 0 ? (
                <p className="text-zinc-400 col-span-4 text-center py-8">No devices available</p>
              ) : (
                devices.map(device => (
                  <div
                    key={device.id}
                    data-testid={`device-status-${device.id}`}
                    className={`p-4 rounded-sm border ${
                      device.status === 'AVAILABLE' ? 'bg-accent-success/10 border-accent-success/30' :
                      device.status === 'OCCUPIED' ? 'bg-accent-warning/10 border-accent-warning/30' :
                      'bg-zinc-800 border-white/10'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-heading font-bold">{device.name}</h3>
                      <div className={`px-2 py-1 rounded-sm text-xs font-mono ${
                        device.status === 'AVAILABLE' ? 'bg-accent-success/20 text-accent-success' :
                        device.status === 'OCCUPIED' ? 'bg-accent-warning/20 text-accent-warning' :
                        'bg-zinc-700 text-zinc-300'
                      }`}>
                        {device.status}
                      </div>
                    </div>
                    <p className="text-sm text-zinc-400">{device.device_type}</p>
                    <p className="text-lg font-heading font-bold text-primary mt-2">₹{device.hourly_rate}/hr</p>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {!activeShift && (
          <Card className="bg-accent-warning/10 border-accent-warning/30 p-4 mt-6">
            <p className="text-accent-warning text-center">
              Please start your shift to begin operations
            </p>
          </Card>
        )}
      </div>
    </div>
  );
};
