import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Clock } from 'lucide-react';

export const SessionTimer = ({ sessionId, startTime, estimatedEndTime }) => {
  const [timeRemaining, setTimeRemaining] = useState('');
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    const calculateTimeRemaining = () => {
      const now = new Date();
      const end = new Date(estimatedEndTime);
      const start = new Date(startTime);
      
      const totalDuration = end - start;
      const elapsed = now - start;
      const remaining = end - now;

      if (remaining <= 0) {
        setTimeRemaining('Session Expired');
        setProgress(0);
        return;
      }

      const hours = Math.floor(remaining / (1000 * 60 * 60));
      const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((remaining % (1000 * 60)) / 1000);

      setTimeRemaining(`${hours}h ${minutes}m ${seconds}s`);
      setProgress(((totalDuration - elapsed) / totalDuration) * 100);
    };

    calculateTimeRemaining();
    const interval = setInterval(calculateTimeRemaining, 1000);

    return () => clearInterval(interval);
  }, [startTime, estimatedEndTime]);

  return (
    <Card className="bg-gradient-to-br from-primary/10 to-surface border-primary/30 p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
          <Clock className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h3 className="font-heading font-bold text-lg">Session Timer</h3>
          <p className="text-xs text-zinc-400">Time Remaining</p>
        </div>
      </div>
      
      <div className="text-center mb-4">
        <p className="text-4xl font-heading font-bold text-primary tabular-nums">
          {timeRemaining}
        </p>
      </div>

      <div className="w-full bg-zinc-800 rounded-full h-3 overflow-hidden">
        <div
          className={`h-3 rounded-full transition-all duration-1000 ${
            progress > 20 ? 'bg-accent-success' : 'bg-accent-error'
          }`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      <div className="mt-4 flex justify-between text-xs text-zinc-400">
        <span>Started: {new Date(startTime).toLocaleTimeString()}</span>
        <span>Ends: {new Date(estimatedEndTime).toLocaleTimeString()}</span>
      </div>
    </Card>
  );
};
