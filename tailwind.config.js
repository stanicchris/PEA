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
        darkBase: '#080A0E',
        darkCanvas: '#05070A',
        darkSurface: 'rgba(18, 22, 30, 0.65)',
        cardMatte: 'rgba(22, 27, 36, 0.55)',
        cardMatteHover: 'rgba(30, 37, 48, 0.75)',
        cardBorder: 'rgba(255, 255, 255, 0.08)',
        neonLime: '#A3E635',
        neonLimeHover: '#B4F59E',
        neonMint: '#86EFAC',
        neonPurple: '#8B5CF6',
        lavender: '#A78BFA',
        lavenderLight: '#C4B5FD',
        roseAcc: '#F43F5E',
        amberAcc: '#F59E0B',
        cyanAcc: '#38BDF8',
      },
      borderRadius: {
        '48': '48px',
        '36': '36px',
        '32': '32px',
        '28': '28px',
        '24': '24px',
        '20': '20px',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'liquid': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.16), inset 0 -1px 1px 0 rgba(0, 0, 0, 0.4), 0 20px 45px -15px rgba(0, 0, 0, 0.65)',
        'liquid-hover': 'inset 0 1px 2px 0 rgba(255, 255, 255, 0.28), inset 0 -1px 1px 0 rgba(0, 0, 0, 0.4), 0 28px 55px -12px rgba(0, 0, 0, 0.8), 0 0 30px rgba(163, 230, 53, 0.06)',
        'liquid-glow-lime': 'inset 0 1px 2px 0 rgba(255, 255, 255, 0.35), 0 15px 40px -10px rgba(163, 230, 53, 0.3)',
        'liquid-glow-purple': 'inset 0 1px 2px 0 rgba(255, 255, 255, 0.35), 0 15px 40px -10px rgba(139, 92, 246, 0.3)',
      }
    },
  },
  plugins: [
    plugin(function({ addUtilities }) {
      addUtilities({
        '.liquid-glass': {
          'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 45%, rgba(10, 14, 20, 0.55) 100%), rgba(16, 21, 29, 0.58)',
          'backdrop-filter': 'blur(26px) saturate(190%) contrast(104%)',
          '-webkit-backdrop-filter': 'blur(26px) saturate(190%) contrast(104%)',
          'border': '1px solid rgba(255, 255, 255, 0.08)',
          'box-shadow': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.16), inset 0 -1px 1px 0 rgba(0, 0, 0, 0.4), 0 20px 45px -15px rgba(0, 0, 0, 0.65)',
          'transition': 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        },
        '.liquid-glass-subtle': {
          'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.035) 0%, rgba(255, 255, 255, 0.01) 50%, rgba(8, 11, 16, 0.4) 100%), rgba(13, 17, 23, 0.45)',
          'backdrop-filter': 'blur(20px) saturate(175%)',
          '-webkit-backdrop-filter': 'blur(20px) saturate(175%)',
          'border': '1px solid rgba(255, 255, 255, 0.06)',
          'box-shadow': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 10px 30px -10px rgba(0, 0, 0, 0.5)',
        },
        '.liquid-glass-pill': {
          'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%), rgba(18, 23, 31, 0.72)',
          'backdrop-filter': 'blur(24px) saturate(190%)',
          '-webkit-backdrop-filter': 'blur(24px) saturate(190%)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
          'box-shadow': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.18), 0 12px 32px -8px rgba(0, 0, 0, 0.6)',
        },
        '.liquid-glass-chassis': {
          'background': 'linear-gradient(180deg, rgba(16, 21, 29, 0.82) 0%, rgba(9, 12, 17, 0.92) 100%)',
          'backdrop-filter': 'blur(36px) saturate(190%)',
          '-webkit-backdrop-filter': 'blur(36px) saturate(190%)',
          'border': '1px solid rgba(255, 255, 255, 0.09)',
          'box-shadow': '0 30px 100px -20px rgba(0, 0, 0, 0.85), inset 0 1px 1px 0 rgba(255, 255, 255, 0.18)',
        },
        /* Backward compatibility aliases */
        '.glass-card': {
          'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 45%, rgba(10, 14, 20, 0.55) 100%), rgba(16, 21, 29, 0.58)',
          'backdrop-filter': 'blur(26px) saturate(190%) contrast(104%)',
          '-webkit-backdrop-filter': 'blur(26px) saturate(190%) contrast(104%)',
          'border': '1px solid rgba(255, 255, 255, 0.08)',
          'box-shadow': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.16), inset 0 -1px 1px 0 rgba(0, 0, 0, 0.4), 0 20px 45px -15px rgba(0, 0, 0, 0.65)',
          'transition': 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        },
        '.glass-card-subtle': {
          'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.035) 0%, rgba(255, 255, 255, 0.01) 50%, rgba(8, 11, 16, 0.4) 100%), rgba(13, 17, 23, 0.45)',
          'backdrop-filter': 'blur(20px) saturate(175%)',
          '-webkit-backdrop-filter': 'blur(20px) saturate(175%)',
          'border': '1px solid rgba(255, 255, 255, 0.06)',
          'box-shadow': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.1), 0 10px 30px -10px rgba(0, 0, 0, 0.5)',
        },
        '.glass-pill': {
          'background': 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%), rgba(18, 23, 31, 0.72)',
          'backdrop-filter': 'blur(24px) saturate(190%)',
          '-webkit-backdrop-filter': 'blur(24px) saturate(190%)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
          'box-shadow': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.18), 0 12px 32px -8px rgba(0, 0, 0, 0.6)',
        }
      })
    })
  ],
}
