import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { TrendingUp, Plus, Edit, Trash2, Calendar, Clock, Tag, Download } from 'lucide-react';

export const PricingControlsPage = () => {
  const [pricingRules, setPricingRules] = useState([]);
  const [coupons, setCoupons] = useState([]);
  const [showRuleDialog, setShowRuleDialog] = useState(false);
  const [showCouponDialog, setShowCouponDialog] = useState(false);
  
  const [ruleForm, setRuleForm] = useState({
    rule_type: 'PEAK',
    multiplier: 1.5,
    start_time: '18:00',
    end_time: '23:00',
    days_of_week: []
  });
  
  const [couponForm, setCouponForm] = useState({
    code: '',
    discount_type: 'percentage',
    discount_value: 10,
    min_amount: 0,
    max_uses: 100,
    valid_days: 30
  });

  useEffect(() => {
    fetchPricingRules();
    fetchCoupons();
  }, []);

  const fetchPricingRules = async () => {
    try {
      const { data } = await api.get('/pricing-rules');
      setPricingRules(data);
    } catch (error) {
      console.error('Failed to fetch pricing rules:', error);
    }
  };

  const fetchCoupons = async () => {
    try {
      const { data } = await api.get('/coupons');
      setCoupons(data || []);
    } catch (error) {
      console.error('Failed to fetch coupons:', error);
    }
  };

  const handleCreateRule = async () => {
    try {
      await api.post('/pricing-rules', ruleForm);
      toast.success('Pricing rule created');
      setShowRuleDialog(false);
      fetchPricingRules();
      setRuleForm({
        rule_type: 'PEAK',
        multiplier: 1.5,
        start_time: '18:00',
        end_time: '23:00',
        days_of_week: []
      });
    } catch (error) {
      toast.error('Failed to create pricing rule');
    }
  };

  const handleCreateCoupon = async () => {
    try {
      await api.post('/coupons', couponForm);
      toast.success('Coupon created');
      setShowCouponDialog(false);
      fetchCoupons();
      setCouponForm({
        code: '',
        discount_type: 'percentage',
        discount_value: 10,
        min_amount: 0,
        max_uses: 100,
        valid_days: 30
      });
    } catch (error) {
      toast.error('Failed to create coupon');
    }
  };

  const handleExportReport = async (type) => {
    try {
      const response = await api.get(`/reports/${type}/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_report.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Report downloaded');
    } catch (error) {
      toast.error('Failed to export report');
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-heading font-bold mb-2">Pricing & Revenue Controls</h1>
            <p className="text-zinc-400">Manage dynamic pricing, coupons, and reports</p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => handleExportReport('sessions')}
            >
              <Download className="w-4 h-4 mr-2" />
              Export Sessions
            </Button>
            <Button
              variant="outline"
              onClick={() => handleExportReport('revenue')}
            >
              <Download className="w-4 h-4 mr-2" />
              Export Revenue
            </Button>
          </div>
        </div>

        {/* Pricing Rules */}
        <Card className="bg-surface border-white/10 p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-heading font-bold">Dynamic Pricing Rules</h2>
            </div>
            <Dialog open={showRuleDialog} onOpenChange={setShowRuleDialog}>
              <DialogTrigger asChild>
                <Button className="bg-primary hover:bg-primary-hover">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Rule
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-surface border-white/10">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-heading">Create Pricing Rule</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Rule Type</label>
                    <Select
                      value={ruleForm.rule_type}
                      onValueChange={(value) => setRuleForm({...ruleForm, rule_type: value})}
                    >
                      <SelectTrigger className="bg-background border-white/10">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="PEAK">Peak Hours</SelectItem>
                        <SelectItem value="OFFPEAK">Off-Peak</SelectItem>
                        <SelectItem value="WEEKEND">Weekend</SelectItem>
                        <SelectItem value="HAPPY_HOUR">Happy Hour</SelectItem>
                        <SelectItem value="FESTIVAL">Festival</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Price Multiplier</label>
                    <Input
                      type="number"
                      step="0.1"
                      value={ruleForm.multiplier}
                      onChange={(e) => setRuleForm({...ruleForm, multiplier: parseFloat(e.target.value)})}
                      className="bg-background border-white/10"
                      placeholder="1.5 for 50% increase, 0.7 for 30% discount"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Start Time</label>
                      <Input
                        type="time"
                        value={ruleForm.start_time}
                        onChange={(e) => setRuleForm({...ruleForm, start_time: e.target.value})}
                        className="bg-background border-white/10"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">End Time</label>
                      <Input
                        type="time"
                        value={ruleForm.end_time}
                        onChange={(e) => setRuleForm({...ruleForm, end_time: e.target.value})}
                        className="bg-background border-white/10"
                      />
                    </div>
                  </div>
                  <Button onClick={handleCreateRule} className="w-full bg-primary hover:bg-primary-hover">
                    Create Rule
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pricingRules.length === 0 ? (
              <p className="text-zinc-400 col-span-2 text-center py-8">No pricing rules configured</p>
            ) : (
              pricingRules.map((rule) => (
                <div
                  key={rule.id}
                  className={`p-4 rounded-sm border ${
                    rule.is_active ? 'bg-primary/10 border-primary/30' : 'bg-zinc-800 border-white/10'
                  }`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-heading font-bold">{rule.rule_type.replace('_', ' ')}</h3>
                      <p className="text-sm text-zinc-400">
                        {rule.start_time} - {rule.end_time}
                      </p>
                    </div>
                    <div className={`px-2 py-1 rounded-sm text-xs font-mono ${
                      rule.is_active ? 'bg-accent-success/20 text-accent-success' : 'bg-zinc-700 text-zinc-400'
                    }`}>
                      {rule.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-primary" />
                    <span className="font-heading font-bold text-lg">
                      {rule.multiplier > 1 ? '+' : ''}{((rule.multiplier - 1) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Coupons */}
        <Card className="bg-surface border-white/10 p-6">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <Tag className="w-6 h-6 text-secondary" />
              <h2 className="text-2xl font-heading font-bold">Coupons & Promotions</h2>
            </div>
            <Dialog open={showCouponDialog} onOpenChange={setShowCouponDialog}>
              <DialogTrigger asChild>
                <Button className="bg-secondary hover:bg-secondary/80">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Coupon
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-surface border-white/10">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-heading">Create Coupon</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Coupon Code</label>
                    <Input
                      value={couponForm.code}
                      onChange={(e) => setCouponForm({...couponForm, code: e.target.value.toUpperCase()})}
                      className="bg-background border-white/10"
                      placeholder="SUMMER50"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Discount Type</label>
                      <Select
                        value={couponForm.discount_type}
                        onValueChange={(value) => setCouponForm({...couponForm, discount_type: value})}
                      >
                        <SelectTrigger className="bg-background border-white/10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="percentage">Percentage</SelectItem>
                          <SelectItem value="fixed">Fixed Amount</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Discount Value</label>
                      <Input
                        type="number"
                        value={couponForm.discount_value}
                        onChange={(e) => setCouponForm({...couponForm, discount_value: parseFloat(e.target.value)})}
                        className="bg-background border-white/10"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Max Uses</label>
                      <Input
                        type="number"
                        value={couponForm.max_uses}
                        onChange={(e) => setCouponForm({...couponForm, max_uses: parseInt(e.target.value)})}
                        className="bg-background border-white/10"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Valid Days</label>
                      <Input
                        type="number"
                        value={couponForm.valid_days}
                        onChange={(e) => setCouponForm({...couponForm, valid_days: parseInt(e.target.value)})}
                        className="bg-background border-white/10"
                      />
                    </div>
                  </div>
                  <Button onClick={handleCreateCoupon} className="w-full bg-secondary hover:bg-secondary/80">
                    Create Coupon
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {coupons.length === 0 ? (
              <p className="text-zinc-400 col-span-3 text-center py-8">No coupons created</p>
            ) : (
              coupons.map((coupon) => (
                <div
                  key={coupon.id}
                  className={`p-4 rounded-sm border ${
                    coupon.is_active ? 'bg-secondary/10 border-secondary/30' : 'bg-zinc-800 border-white/10'
                  }`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-mono font-bold text-xl">{coupon.code}</h3>
                    <div className={`px-2 py-1 rounded-sm text-xs font-mono ${
                      coupon.is_active ? 'bg-accent-success/20 text-accent-success' : 'bg-zinc-700 text-zinc-400'
                    }`}>
                      {coupon.is_active ? 'ACTIVE' : 'EXPIRED'}
                    </div>
                  </div>
                  <p className="text-2xl font-heading font-bold text-secondary mb-2">
                    {coupon.discount_type === 'percentage' ? `${coupon.discount_value}% OFF` : `₹${coupon.discount_value} OFF`}
                  </p>
                  <div className="text-xs text-zinc-400 space-y-1">
                    <p>Used: {coupon.used_count}/{coupon.max_uses || '∞'}</p>
                    <p>Expires: {new Date(coupon.valid_until).toLocaleDateString()}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};
