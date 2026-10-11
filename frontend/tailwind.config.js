/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: '#FDFBF7',
          100: '#FAF8F3', // Primary page background
          200: '#F5F1E6', // Section container
          300: '#EFE9D9',
          400: '#E4DAC4',
          500: '#D5C7AA',
        },
        medyellow: {
          50: '#FFFDEB',
          100: '#FEF9C3', // Accent tint
          200: '#FEF08A',
          300: '#FDE047',
          400: '#FACC15',
        },
        clinical: {
          green: {
            light: '#86EFAC',
            DEFAULT: '#10B981',
            hover: '#059669',
            dark: '#047857',
          },
          black: {
            DEFAULT: '#18181B',
            hover: '#09090B',
            card: '#27272A',
          },
          red: {
            bg: '#FEF2F2',
            border: '#FECACA',
            text: '#991B1B',
            solid: '#DC2626',
            badge: '#B91C1C',
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(180, 160, 130, 0.08)',
        'alert': '0 4px 25px -3px rgba(220, 38, 38, 0.15)',
      }
    },
  },
  plugins: [],
}

