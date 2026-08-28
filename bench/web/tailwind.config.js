/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ocean: {
          950: '#050B14',
          900: '#071324',
          850: '#0A1B33',
          800: '#0F274A',
          700: '#163B6F',
        },
        cyan: {
          400: '#22D3EE',
          500: '#06B6D4',
          600: '#0891B2',
          700: '#0E7490',
        },
        sand: {
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      backgroundImage: {
        'ocean-radial': 'radial-gradient(ellipse at top, #0c4a6e 0%, #071324 60%, #050B14 100%)',
        'wave-glow': 'radial-gradient(circle at 50% 0%, rgba(6, 182, 212, 0.15), transparent 70%)',
      }
    },
  },
  plugins: [],
}
