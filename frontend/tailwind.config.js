/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Chakra Petch', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: '0.125rem'
      },
      colors: {
        background: '#09090b',
        surface: '#18181b',
        foreground: '#ffffff',
        card: {
          DEFAULT: '#18181b',
          foreground: '#ffffff'
        },
        popover: {
          DEFAULT: '#18181b',
          foreground: '#ffffff'
        },
        primary: {
          DEFAULT: '#7c3aed',
          hover: '#6d28d9',
          foreground: '#ffffff'
        },
        secondary: {
          DEFAULT: '#06b6d4',
          foreground: '#ffffff'
        },
        muted: {
          DEFAULT: '#27272a',
          foreground: '#a1a1aa'
        },
        accent: {
          DEFAULT: '#27272a',
          foreground: '#ffffff',
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6'
        },
        destructive: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff'
        },
        border: 'rgba(255, 255, 255, 0.1)',
        input: 'rgba(255, 255, 255, 0.1)',
        ring: '#7c3aed',
        chart: {
          '1': '#7c3aed',
          '2': '#06b6d4',
          '3': '#10b981',
          '4': '#f59e0b',
          '5': '#ef4444'
        }
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        },
        'pulse-slow': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' }
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'pulse-slow': 'pulse-slow 3s ease-in-out infinite'
      },
      boxShadow: {
        'glow': '0 0 20px -5px rgba(124, 58, 237, 0.5)',
        'glow-cyan': '0 0 20px -5px rgba(6, 182, 212, 0.5)'
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};
