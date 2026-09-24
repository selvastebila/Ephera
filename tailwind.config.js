/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        vault: {
          950: '#060913',
          900: '#0b0f19',
          850: '#111827',
          800: '#1f293d',
          700: '#334155',
          cyan: '#00f0ff',
          emerald: '#10b981',
          accent: '#06b6d4',
          alert: '#ef4444',
          warn: '#f59e0b'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-cyan': '0 0 25px -5px rgba(0, 240, 255, 0.3)',
        'glow-emerald': '0 0 25px -5px rgba(16, 185, 129, 0.3)',
        'glow-alert': '0 0 25px -5px rgba(239, 68, 68, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 3s ease-in-out infinite',
      },
      keyframes: {
        scan: {
          '0%, 100%': { transform: 'translateY(0%)' },
          '50%': { transform: 'translateY(100%)' },
        }
      }
    },
  },
  plugins: [],
}
