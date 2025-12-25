import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { MapPin, Clock, Star, Gamepad2, Phone, ArrowLeft } from 'lucide-react';

export const CafeProfilePage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [cafe, setCafe] = useState(null);
  const [devices, setDevices] = useState([]);
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCafeData();
  }, [slug]);

  const fetchCafeData = async () => {
    try {
      // Get all cafes and find by slug
      const { data: cafes } = await api.get('/cafes/public');
      const cafeData = cafes.find(c => c.slug === slug);
      
      if (cafeData) {
        setCafe(cafeData);
        
        // Get devices
        const { data: devicesData } = await api.get(`/devices?cafe_id=${cafeData.id}`);
        setDevices(devicesData);
        
        // Get games
        const { data: gamesData } = await api.get(`/games?cafe_id=${cafeData.id}`);
        setGames(gamesData);
      }
    } catch (error) {
      console.error('Failed to fetch cafe data:', error);
    } finally {
      setLoading(false);
    }
  };

  const availableDevices = devices.filter(d => d.status === 'AVAILABLE');

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!cafe) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-heading font-bold text-primary mb-4">Café Not Found</h1>
          <Button onClick={() => navigate('/')}>Go Home</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div
        className="relative h-96 bg-cover bg-center"
        style={{
          backgroundImage: `url(https://images.pexels.com/photos/3945683/pexels-photo-3945683.jpeg)`,
        }}
      >
        <div className="absolute inset-0 bg-black/70"></div>
        <div className="relative z-10 max-w-7xl mx-auto px-6 h-full flex flex-col justify-center">
          <Button
            variant="ghost"
            className="w-fit mb-6"
            onClick={() => navigate('/')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-5xl md:text-6xl font-heading font-bold text-white mb-4">
            {cafe.name}
          </h1>
          <div className="flex flex-wrap items-center gap-6 text-white">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              <span>{cafe.address}, {cafe.city}</span>
            </div>
            <div className="flex items-center gap-2">
              <Gamepad2 className="w-5 h-5" />
              <span>{devices.length} Devices</span>
            </div>
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 fill-accent-warning text-accent-warning" />
              <span>4.8 Rating</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* About */}
            {cafe.description && (
              <Card className="bg-surface border-white/10 p-6">
                <h2 className="text-2xl font-heading font-bold mb-4">About This Café</h2>
                <p className="text-zinc-300 leading-relaxed">{cafe.description}</p>
              </Card>
            )}

            {/* Available Devices */}
            <Card className="bg-surface border-white/10 p-6">
              <h2 className="text-2xl font-heading font-bold mb-4">Available Now</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableDevices.length === 0 ? (
                  <p className="text-zinc-400 col-span-2 text-center py-8">No devices available at the moment</p>
                ) : (
                  availableDevices.map(device => (
                    <div
                      key={device.id}
                      className="p-4 bg-accent-success/10 border border-accent-success/30 rounded-sm"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-heading font-bold">{device.name}</h3>
                          <p className="text-sm text-zinc-400">{device.device_type}</p>
                        </div>
                        <div className="px-2 py-1 bg-accent-success/20 text-accent-success rounded-sm text-xs font-mono">
                          AVAILABLE
                        </div>
                      </div>
                      <p className="text-2xl font-heading font-bold text-primary">₹{device.hourly_rate}/hr</p>
                      {device.specifications && (
                        <p className="text-xs text-zinc-400 mt-2">{device.specifications}</p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </Card>

            {/* Games Available */}
            {games.length > 0 && (
              <Card className="bg-surface border-white/10 p-6">
                <h2 className="text-2xl font-heading font-bold mb-4">Popular Games</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {games.slice(0, 8).map(game => (
                    <div key={game.id} className="text-center">
                      <div className="w-full aspect-square bg-primary/10 rounded-sm mb-2 flex items-center justify-center">
                        <Gamepad2 className="w-8 h-8 text-primary" />
                      </div>
                      <p className="text-sm font-medium">{game.name}</p>
                      <p className="text-xs text-zinc-400">{game.genre}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card className="bg-gradient-to-br from-primary/10 to-surface border-primary/30 p-6">
              <h3 className="text-xl font-heading font-bold mb-4">Quick Info</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Total Devices</span>
                  <span className="font-heading font-bold text-xl">{devices.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Available Now</span>
                  <span className="font-heading font-bold text-xl text-accent-success">{availableDevices.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">Games Library</span>
                  <span className="font-heading font-bold text-xl">{games.length}</span>
                </div>
              </div>
            </Card>

            {/* Call to Action */}
            <Card className="bg-surface border-white/10 p-6">
              <h3 className="text-xl font-heading font-bold mb-4">Ready to Play?</h3>
              <p className="text-zinc-400 mb-6">Login to book devices and start your gaming session</p>
              <Button
                onClick={() => navigate('/login')}
                className="w-full bg-primary hover:bg-primary-hover"
              >
                Login to Book
              </Button>
            </Card>

            {/* Opening Hours */}
            <Card className="bg-surface border-white/10 p-6">
              <h3 className="text-xl font-heading font-bold mb-4">Opening Hours</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-zinc-400">Monday - Friday</span>
                  <span className="font-medium">10:00 AM - 11:00 PM</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Saturday - Sunday</span>
                  <span className="font-medium">9:00 AM - 12:00 AM</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};
