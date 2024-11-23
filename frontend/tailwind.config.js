/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          DEFAULT: '#0B1120',
          lighter: '#141B2D',
          card: '#1F2937',
          border: '#374151'
        }
      },
      backgroundColor: {
        primary: '#2563EB',
        secondary: '#4B5563'
      }
    },
  },
  plugins: [],
} 