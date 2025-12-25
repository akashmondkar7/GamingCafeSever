import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { Crown, Wallet, Gift, TrendingUp, Clock, Calendar } from 'lucide-react';

export const MembershipPage = () => {
  const { user } = useAuth();
  const [membership, setMembership] = useState(null);
  const [passes, setPasses] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [selectedPass, setSelectedPass] = useState(null);

  useEffect(() => {
    fetchMembership();
    fetchPasses();
    fetchTransactions();
  }, []);

  const fetchMembership = async () => {
    try {
      const { data } = await api.get('/membership/my');
      setMembership(data);
    } catch (error) {
      console.error('Failed to fetch membership:', error);
    }
  };

  const fetchPasses = async () => {
    try {
      const { data } = await api.get('/membership/passes');
      setPasses(data);
    } catch (error) {
      console.error('Failed to fetch passes:', error);
    }
  };

  const fetchTransactions = async () => {
    try {
      const { data } = await api.get('/wallet/transactions');
      setTransactions(data);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    }
  };

  const handleAddMoney = async (amount) => {
    try {
      await api.post(`/wallet/add-money?amount=${amount}`);
      toast.success(`Added ₹${amount} to wallet`);
      fetchTransactions();
      // Refresh user data
      window.location.reload();
    } catch (error) {
      toast.error('Failed to add money');
    }
  };

  const handlePurchasePass = async (passType, cafeId = 'default') => {
    try {
      await api.post('/membership/purchase-pass', { pass_type: passType, cafe_id: cafeId });
      toast.success('Pass purchased successfully');
      fetchPasses();
      fetchTransactions();
      window.location.reload();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to purchase pass');
    }
  };

  const getTierColor = (tier) => {
    switch(tier) {
      case 'PLATINUM': return 'from-zinc-200 to-zinc-400';
      case 'GOLD': return 'from-accent-warning to-yellow-600';
      case 'SILVER': return 'from-zinc-400 to-zinc-500';
      default: return 'from-amber-700 to-amber-900';
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Membership Card */}
        <Card className={`bg-gradient-to-br ${membership ? getTierColor(membership.tier) : 'from-primary to-purple-900'} p-8 mb-8 relative overflow-hidden`}>
          <div className="relative z-10">
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <Crown className="w-8 h-8 text-white" />
                  <h2 className="text-3xl font-heading font-bold text-white">{membership?.tier || 'BRONZE'} MEMBER</h2>
                </div>
                <p className="text-white/80 text-lg">{user?.name}</p>
              </div>
              <div className="text-right">
                <p className="text-white/80 text-sm mb-1">Wallet Balance</p>
                <p className="text-4xl font-heading font-bold text-white">₹{user?.wallet_balance || 0}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-6 text-white">
              <div>
                <p className="text-white/80 text-sm mb-1">Points</p>
                <p className="text-2xl font-heading font-bold">{membership?.points || 0}</p>
              </div>
              <div>
                <p className="text-white/80 text-sm mb-1">Total Spent</p>
                <p className="text-2xl font-heading font-bold">₹{membership?.total_spent || 0}</p>
              </div>
              <div>
                <p className="text-white/80 text-sm mb-1">Total Hours</p>
                <p className="text-2xl font-heading font-bold">{membership?.total_hours || 0}h</p>
              </div>
            </div>
            {membership?.referral_code && (
              <div className="mt-6 p-4 bg-black/20 rounded-sm">
                <p className="text-white/80 text-sm mb-1">Your Referral Code</p>
                <p className="text-2xl font-mono font-bold text-white tracking-wider">{membership.referral_code}</p>
              </div>
            )}
          </div>
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Add Money */}
          <Card className="bg-surface border-white/10 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Wallet className="w-6 h-6 text-primary" />
              <h3 className="text-2xl font-heading font-bold">Add Money to Wallet</h3>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Button onClick={() => handleAddMoney(500)} className="bg-primary hover:bg-primary-hover">
                + ₹500
              </Button>
              <Button onClick={() => handleAddMoney(1000)} className="bg-primary hover:bg-primary-hover">
                + ₹1000
              </Button>
              <Button onClick={() => handleAddMoney(2000)} className="bg-primary hover:bg-primary-hover">
                + ₹2000
              </Button>
              <Button onClick={() => handleAddMoney(5000)} className="bg-primary hover:bg-primary-hover">
                + ₹5000
              </Button>
            </div>
          </Card>

          {/* Purchase Passes */}
          <Card className="bg-surface border-white/10 p-6">
            <div className="flex items-center gap-3 mb-6">
              <Clock className="w-6 h-6 text-secondary" />
              <h3 className="text-2xl font-heading font-bold">Buy Gaming Passes</h3>
            </div>
            <div className="space-y-3">
              <Button onClick={() => handlePurchasePass('HOURLY')} variant="outline" className="w-full justify-between">
                <span>Hourly Pass - 1 hour</span>
                <span className="font-bold">₹100</span>
              </Button>
              <Button onClick={() => handlePurchasePass('DAILY')} variant="outline" className="w-full justify-between">
                <span>Daily Pass - 8 hours</span>
                <span className="font-bold">₹500</span>
              </Button>
              <Button onClick={() => handlePurchasePass('WEEKLY')} variant="outline" className="w-full justify-between">
                <span>Weekly Pass - 50 hours</span>
                <span className="font-bold">₹2,500</span>
              </Button>
              <Button onClick={() => handlePurchasePass('MONTHLY')} variant="outline" className="w-full justify-between">
                <span>Monthly Pass - 200 hours</span>
                <span className="font-bold">₹8,000</span>
              </Button>
            </div>
          </Card>
        </div>

        {/* Active Passes */}
        <Card className="bg-surface border-white/10 p-6 mb-8">
          <h3 className="text-2xl font-heading font-bold mb-6">My Passes</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {passes.length === 0 ? (
              <p className="text-zinc-400 col-span-3 text-center py-8">No active passes</p>
            ) : (
              passes.map(pass => (
                <div key={pass.id} className={`p-4 rounded-sm border ${
                  pass.is_active ? 'bg-accent-success/10 border-accent-success/30' : 'bg-zinc-800 border-white/10'
                }`}>
                  <div className="flex justify-between items-start mb-3">
                    <Calendar className="w-5 h-5 text-primary" />
                    <span className={`px-2 py-1 rounded-sm text-xs font-mono ${
                      pass.is_active ? 'bg-accent-success/20 text-accent-success' : 'bg-zinc-700 text-zinc-400'
                    }`}>
                      {pass.is_active ? 'ACTIVE' : 'EXPIRED'}
                    </span>
                  </div>
                  <h4 className="font-heading font-bold mb-2">{pass.pass_type} Pass</h4>
                  <div className="text-sm text-zinc-400 space-y-1">
                    <p>Hours: {pass.hours_used}/{pass.hours_included}</p>
                    <p>Valid until: {new Date(pass.valid_until).toLocaleDateString()}</p>
                  </div>
                  <div className="mt-3 w-full bg-zinc-700 rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${(pass.hours_used / pass.hours_included) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Transaction History */}
        <Card className="bg-surface border-white/10 p-6">
          <h3 className="text-2xl font-heading font-bold mb-6">Transaction History</h3>
          <div className="space-y-3">
            {transactions.length === 0 ? (
              <p className="text-zinc-400 text-center py-8">No transactions yet</p>
            ) : (
              transactions.slice(0, 10).map(txn => (
                <div key={txn.id} className="flex items-center justify-between p-4 bg-background rounded-sm border border-white/5">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-sm flex items-center justify-center ${
                      txn.transaction_type === 'credit' ? 'bg-accent-success/20' : 'bg-accent-error/20'
                    }`}>
                      <TrendingUp className={`w-5 h-5 ${
                        txn.transaction_type === 'credit' ? 'text-accent-success' : 'text-accent-error'
                      }`} />
                    </div>
                    <div>
                      <p className="font-medium">{txn.description}</p>
                      <p className="text-xs text-zinc-400">{new Date(txn.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <p className={`text-lg font-heading font-bold ${
                    txn.transaction_type === 'credit' ? 'text-accent-success' : 'text-accent-error'
                  }`}>
                    {txn.transaction_type === 'credit' ? '+' : ''}₹{Math.abs(txn.amount)}
                  </p>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
