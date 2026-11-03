/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0B0E14',
        surface: '#121721',
        card: '#181F2C',
        border: '#232D3F',
        bullish: '#10B981',
        bearish: '#EF4444',
        accent: '#3B82F6',
        neutral: '#9CA3AF'
      }
    },
  },
  plugins: [],
}
