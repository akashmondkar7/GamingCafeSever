import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const LoginPage = () => {
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [mockOtp, setMockOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/login`, { phone });
      setMockOtp(response.data.mock_otp);
      setOtpSent(true);
      toast.success(`OTP sent: ${response.data.mock_otp}`);
    } catch (error) {
      toast.error('Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/verify-otp`, { phone, otp });
      login(response.data.token, response.data.user);
      toast.success('Login successful!');
      
      // Navigate based on role
      const role = response.data.user.role;
      if (role === 'SUPER_ADMIN') {
        navigate('/admin');
      } else if (role === 'CAFE_OWNER') {
        navigate('/owner');
      } else if (role === 'STAFF') {
        navigate('/staff');
      } else {
        navigate('/customer');
      }
    } catch (error) {
      toast.error('Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 bg-surface border-white/10" data-testid="login-card">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-heading font-bold text-primary mb-2">GAME CAFÉ</h1>
          <p className="text-zinc-400">Smart Gaming Café Management</p>
        </div>

        {!otpSent ? (
          <form onSubmit={handleSendOtp} className="space-y-4">
            <div>
              <Label htmlFor="phone" className="text-zinc-300">Phone Number</Label>
              <Input
                id="phone"
                data-testid="phone-input"
                type="tel"
                placeholder="Enter your phone number"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="mt-1 bg-background border-white/10 focus:border-primary"
                required
              />
            </div>
            <Button
              data-testid="send-otp-button"
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover"
              disabled={loading}
            >
              {loading ? 'Sending...' : 'Send OTP'}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div className="bg-primary/10 border border-primary/30 rounded-sm p-3 mb-4">
              <p className="text-xs text-zinc-400 mb-1">Mock OTP for Testing:</p>
              <p className="text-lg font-mono text-primary font-bold">{mockOtp}</p>
            </div>
            <div>
              <Label htmlFor="otp" className="text-zinc-300">Enter OTP</Label>
              <Input
                id="otp"
                data-testid="otp-input"
                type="text"
                placeholder="Enter 6-digit OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="mt-1 bg-background border-white/10 focus:border-primary"
                maxLength={6}
                required
              />
            </div>
            <Button
              data-testid="verify-otp-button"
              type="submit"
              className="w-full bg-primary hover:bg-primary-hover"
              disabled={loading}
            >
              {loading ? 'Verifying...' : 'Verify & Login'}
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="w-full"
              onClick={() => setOtpSent(false)}
            >
              Change Phone Number
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
};
