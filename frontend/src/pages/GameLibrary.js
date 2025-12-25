import React, { useState, useEffect } from 'react';
import { useAuth, api } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Gamepad, Plus, Star, Info } from 'lucide-react';

export const GameLibrary = () => {
  const { user } = useAuth();
  const [games, setGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    genre: '',
    description: '',
    device_types: [],
    how_to_start: '',
    controls_guide: '',
    difficulty_level: 'MEDIUM',
    age_rating: 'EVERYONE'
  });

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      const { data } = await api.get('/games');
      setGames(data);
    } catch (error) {
      console.error('Failed to fetch games:', error);
    }
  };

  const handleAddGame = async () => {
    try {
      await api.post('/games', formData);
      toast.success('Game added to library');
      setShowAddDialog(false);
      fetchGames();
      setFormData({
        name: '',
        genre: '',
        description: '',
        device_types: [],
        how_to_start: '',
        controls_guide: '',
        difficulty_level: 'MEDIUM',
        age_rating: 'EVERYONE'
      });
    } catch (error) {
      toast.error('Failed to add game');
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-heading font-bold mb-2">Game Library</h1>
            <p className="text-zinc-400">Manage your gaming catalog</p>
          </div>
          {user?.role === 'CAFE_OWNER' && (
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogTrigger asChild>
                <Button className="bg-primary hover:bg-primary-hover">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Game
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-surface border-white/10 max-w-2xl">
                <DialogHeader>
                  <DialogTitle className="text-2xl font-heading">Add New Game</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Game Name</label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="bg-background border-white/10"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Genre</label>
                      <Input
                        value={formData.genre}
                        onChange={(e) => setFormData({...formData, genre: e.target.value})}
                        className="bg-background border-white/10"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-zinc-400 mb-2 block">Difficulty</label>
                      <Select
                        value={formData.difficulty_level}
                        onValueChange={(value) => setFormData({...formData, difficulty_level: value})}
                      >
                        <SelectTrigger className="bg-background border-white/10">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="EASY">Easy</SelectItem>
                          <SelectItem value="MEDIUM">Medium</SelectItem>
                          <SelectItem value="HARD">Hard</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Description</label>
                    <Textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="bg-background border-white/10"
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">How to Start</label>
                    <Textarea
                      value={formData.how_to_start}
                      onChange={(e) => setFormData({...formData, how_to_start: e.target.value})}
                      className="bg-background border-white/10"
                      rows={2}
                    />
                  </div>
                  <div>
                    <label className="text-sm text-zinc-400 mb-2 block">Controls Guide</label>
                    <Textarea
                      value={formData.controls_guide}
                      onChange={(e) => setFormData({...formData, controls_guide: e.target.value})}
                      className="bg-background border-white/10"
                      rows={3}
                    />
                  </div>
                  <Button onClick={handleAddGame} className="w-full bg-primary hover:bg-primary-hover">
                    Add to Library
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>

        {/* Games Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {games.length === 0 ? (
            <div className="col-span-4 text-center py-20">
              <Gamepad className="w-16 h-16 text-zinc-600 mx-auto mb-4" />
              <p className="text-zinc-400 text-lg">No games in library yet</p>
            </div>
          ) : (
            games.map(game => (
              <Card
                key={game.id}
                className="bg-surface border-white/10 p-6 cursor-pointer hover:border-primary/50 transition-all"
                onClick={() => setSelectedGame(game)}
              >
                <div className="flex justify-between items-start mb-4">
                  <Gamepad className="w-10 h-10 text-primary" />
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-accent-warning fill-accent-warning" />
                    <span className="text-sm font-mono">{game.popularity_score || 0}</span>
                  </div>
                </div>
                <h3 className="font-heading font-bold text-lg mb-2">{game.name}</h3>
                <p className="text-sm text-zinc-400 mb-3">{game.genre}</p>
                <div className="flex items-center gap-2 text-xs">
                  <span className="px-2 py-1 bg-primary/20 text-primary rounded-sm">{game.age_rating}</span>
                  {game.difficulty_level && (
                    <span className="px-2 py-1 bg-secondary/20 text-secondary rounded-sm">{game.difficulty_level}</span>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>

        {/* Game Detail Modal */}
        {selectedGame && (
          <Dialog open={!!selectedGame} onOpenChange={() => setSelectedGame(null)}>
            <DialogContent className="bg-surface border-white/10 max-w-3xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-3xl font-heading">{selectedGame.name}</DialogTitle>
              </DialogHeader>
              <div className="space-y-6 mt-4">
                <div className="flex gap-4">
                  <span className="px-3 py-1 bg-primary/20 text-primary rounded-sm font-mono">{selectedGame.genre}</span>
                  <span className="px-3 py-1 bg-secondary/20 text-secondary rounded-sm font-mono">{selectedGame.age_rating}</span>
                  {selectedGame.difficulty_level && (
                    <span className="px-3 py-1 bg-accent-warning/20 text-accent-warning rounded-sm font-mono">
                      {selectedGame.difficulty_level}
                    </span>
                  )}
                </div>

                {selectedGame.description && (
                  <div>
                    <h4 className="font-heading font-bold text-lg mb-2">Description</h4>
                    <p className="text-zinc-300">{selectedGame.description}</p>
                  </div>
                )}

                {selectedGame.how_to_start && (
                  <div className="bg-primary/10 border border-primary/30 rounded-sm p-4">
                    <h4 className="font-heading font-bold text-lg mb-2 flex items-center gap-2">
                      <Info className="w-5 h-5" />
                      How to Start
                    </h4>
                    <p className="text-zinc-300 whitespace-pre-wrap">{selectedGame.how_to_start}</p>
                  </div>
                )}

                {selectedGame.controls_guide && (
                  <div className="bg-secondary/10 border border-secondary/30 rounded-sm p-4">
                    <h4 className="font-heading font-bold text-lg mb-2">Controls Guide</h4>
                    <p className="text-zinc-300 whitespace-pre-wrap">{selectedGame.controls_guide}</p>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  );
};
