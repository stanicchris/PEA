import plugin from 'tailwindcss/plugin';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0E1117',
        foreground: '#F8FAFC',
        emerald: {
          DEFAULT: '#10B981',
        },
        rose: {
          DEFAULT: '#F43F5E',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [
    plugin(function({ addUtilities }) {
      addUtilities({
        '.glass': {
          'background-color': 'rgba(21, 25, 33, 0.5)', /* Translucent dark surface */
          'backdrop-filter': 'blur(16px)',
          '-webkit-backdrop-filter': 'blur(16px)',
          'border': '1px solid rgba(255, 255, 255, 0.05)', /* 1px subtle white border */
        }
      })
    })
  ],
}
