import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Gamepad2, TrendingUp, Users, Cpu, Shield, Zap } from 'lucide-react';

export const LandingPage = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center overflow-hidden">
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: 'url(https://images.pexels.com/photos/7849505/pexels-photo-7849505.jpeg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          <div className="absolute inset-0 bg-black/80"></div>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
            <div className="md:col-span-8">
              <p className="text-secondary text-xs uppercase tracking-widest font-mono mb-4" data-testid="hero-tagline">
                AI-POWERED SAAS PLATFORM
              </p>
              <h1 className="text-5xl md:text-7xl font-heading font-bold tracking-tight leading-none mb-6" data-testid="hero-title">
                The Operating System for
                <span className="block text-primary mt-2">Gaming Cafés</span>
              </h1>
              <p className="text-lg md:text-xl text-zinc-300 leading-relaxed mb-8 max-w-2xl" data-testid="hero-description">
                Automate operations, maximize revenue, and scale your gaming café empire with AI-powered insights and smart automation.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link to="/login">
                  <Button data-testid="get-started-button" size="lg" className="bg-primary hover:bg-primary-hover shadow-glow text-base px-8">
                    GET STARTED
                  </Button>
                </Link>
                <Link to="#pricing">
                  <Button data-testid="view-pricing-button" size="lg" variant="outline" className="border-white/20 hover:border-primary text-base px-8">
                    VIEW PRICING
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 md:py-32 bg-surface" data-testid="features-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <p className="text-secondary text-xs uppercase tracking-widest font-mono mb-4">CORE FEATURES</p>
            <h2 className="text-3xl md:text-5xl font-heading font-bold tracking-tight">Built for Scale & Automation</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-background border border-white/10 p-6 md:p-8 rounded-sm hover:border-primary/50 transition-colors" data-testid="feature-ai-agents">
              <Cpu className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-2xl font-heading font-semibold mb-3">7 AI Agents</h3>
              <p className="text-zinc-400 leading-relaxed">
                Smart pricing, device optimization, customer behavior analysis, fraud detection, and automated operations.
              </p>
            </div>

            <div className="bg-background border border-white/10 p-6 md:p-8 rounded-sm hover:border-primary/50 transition-colors" data-testid="feature-realtime-booking">
              <Gamepad2 className="w-12 h-12 text-secondary mb-4" />
              <h3 className="text-2xl font-heading font-semibold mb-3">Real-Time Booking</h3>
              <p className="text-zinc-400 leading-relaxed">
                Live slot management, QR check-in, auto session tracking, and dynamic pricing for peak hours.
              </p>
            </div>

            <div className="bg-background border border-white/10 p-6 md:p-8 rounded-sm hover:border-primary/50 transition-colors" data-testid="feature-multi-tenant">
              <TrendingUp className="w-12 h-12 text-accent-success mb-4" />
              <h3 className="text-2xl font-heading font-semibold mb-3">Multi-Tenant SaaS</h3>
              <p className="text-zinc-400 leading-relaxed">
                Manage multiple cafés, franchises, and branches from one unified dashboard with subscription billing.
              </p>
            </div>

            <div className="bg-background border border-white/10 p-6 md:p-8 rounded-sm hover:border-primary/50 transition-colors" data-testid="feature-device-management">
              <Zap className="w-12 h-12 text-accent-warning mb-4" />
              <h3 className="text-2xl font-heading font-semibold mb-3">Device Management</h3>
              <p className="text-zinc-400 leading-relaxed">
                Track PC, PS5, VR, and simulators. Monitor health, maintenance, and peak usage patterns.
              </p>
            </div>

            <div className="bg-background border border-white/10 p-6 md:p-8 rounded-sm hover:border-primary/50 transition-colors" data-testid="feature-analytics">
              <Users className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-2xl font-heading font-semibold mb-3">Advanced Analytics</h3>
              <p className="text-zinc-400 leading-relaxed">
                Revenue insights, customer segmentation, utilization heatmaps, and predictive analytics.
              </p>
            </div>

            <div className="bg-background border border-white/10 p-6 md:p-8 rounded-sm hover:border-primary/50 transition-colors" data-testid="feature-security">
              <Shield className="w-12 h-12 text-accent-error mb-4" />
              <h3 className="text-2xl font-heading font-semibold mb-3">Enterprise Security</h3>
              <p className="text-zinc-400 leading-relaxed">
                Role-based access, audit logs, fraud detection, and automated compliance reporting.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 md:py-32 bg-background" data-testid="pricing-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <p className="text-secondary text-xs uppercase tracking-widest font-mono mb-4">PRICING PLANS</p>
            <h2 className="text-3xl md:text-5xl font-heading font-bold tracking-tight mb-4">Choose Your Plan</h2>
            <p className="text-zinc-400 text-lg">7-day free trial • No credit card required</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* BASIC Plan */}
            <div className="bg-surface border border-white/10 rounded-sm p-8 hover:border-white/20 transition-colors" data-testid="pricing-basic">
              <h3 className="text-2xl font-heading font-bold mb-2">BASIC</h3>
              <div className="mb-6">
                <span className="text-5xl font-heading font-bold">₹1,999</span>
                <span className="text-zinc-400">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Up to 10 devices</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Booking & billing</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Basic analytics</span>
                </li>
              </ul>
              <Link to="/login">
                <Button className="w-full" variant="outline">START TRIAL</Button>
              </Link>
            </div>

            {/* PRO Plan */}
            <div className="bg-gradient-to-b from-primary/10 to-surface border border-primary rounded-sm p-8 relative" data-testid="pricing-pro">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary px-4 py-1 rounded-sm text-xs font-mono uppercase">
                MOST POPULAR
              </div>
              <h3 className="text-2xl font-heading font-bold mb-2">PRO</h3>
              <div className="mb-6">
                <span className="text-5xl font-heading font-bold">₹3,999</span>
                <span className="text-zinc-400">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Up to 25 devices</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Full AI assistant</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Smart pricing engine</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Membership system</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Advanced analytics</span>
                </li>
              </ul>
              <Link to="/login">
                <Button className="w-full bg-primary hover:bg-primary-hover shadow-glow">START TRIAL</Button>
              </Link>
            </div>

            {/* ENTERPRISE Plan */}
            <div className="bg-surface border border-white/10 rounded-sm p-8 hover:border-white/20 transition-colors" data-testid="pricing-enterprise">
              <h3 className="text-2xl font-heading font-bold mb-2">ENTERPRISE</h3>
              <div className="mb-6">
                <span className="text-5xl font-heading font-bold">Custom</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Unlimited devices</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Multiple branches</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">All AI agents</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Franchise dashboard</span>
                </li>
                <li className="flex items-start">
                  <span className="text-accent-success mr-2">✓</span>
                  <span className="text-zinc-300">Dedicated support</span>
                </li>
              </ul>
              <Link to="/login">
                <Button className="w-full" variant="outline">CONTACT SALES</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-surface border-t border-white/10 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-zinc-400">© 2025 Game Café OS. Built with AI for the future of gaming cafés.</p>
        </div>
      </footer>
    </div>
  );
};
