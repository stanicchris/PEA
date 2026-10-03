import plugin from 'tailwindcss/plugin';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkBase: '#0C0E12',
        darkCanvas: '#080A0E',
        darkSurface: '#121418',
        cardMatte: '#16191E',
        cardMatteHover: '#1B1F26',
        cardBorder: 'rgba(255, 255, 255, 0.07)',
        neonLime: '#A3E635',
        neonLimeHover: '#B4F59E',
        neonMint: '#98F794',
        neonPurple: '#8B5CF6',
        lavender: '#A78BFA',
        lavenderLight: '#C4B5FD',
        roseAcc: '#F43F5E',
        amberAcc: '#F59E0B',
      },
      borderRadius: {
        '48': '48px',
        '36': '36px',
        '32': '32px',
        '28': '28px',
        '24': '24px',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [
    plugin(function({ addUtilities }) {
      addUtilities({
        '.glass-card': {
          'background-color': '#16191E',
          'border': '1px solid rgba(255, 255, 255, 0.07)',
          'box-shadow': '0 20px 40px -15px rgba(0, 0, 0, 0.5)',
        },
        '.glass-card-subtle': {
          'background-color': '#111419',
          'border': '1px solid rgba(255, 255, 255, 0.05)',
        },
        '.glass-pill': {
          'background-color': 'rgba(22, 25, 30, 0.85)',
          'backdrop-filter': 'blur(16px)',
          '-webkit-backdrop-filter': 'blur(16px)',
          'border': '1px solid rgba(255, 255, 255, 0.08)',
        }
      })
    })
  ],
}
