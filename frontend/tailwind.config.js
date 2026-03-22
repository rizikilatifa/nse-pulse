/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        nse: {
          primary: '#1a365d',
          secondary: '#2d3748',
          accent: '#48bb78',
          positive: '#22c55e',
          negative: '#ef4444',
          neutral: '#f59e0b',
        }
      }
    },
  },
  plugins: [],
}
