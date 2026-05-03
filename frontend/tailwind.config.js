/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jarvis: {
          dark: '#0a0a0f',
          panel: 'rgba(15, 20, 30, 0.65)',
          border: 'rgba(0, 200, 255, 0.2)',
          highlight: '#00c8ff',
          alert: '#ff3366',
          success: '#00ff99'
        }
      },
      animation: {
        'radar-spin': 'spin 4s linear infinite',
        'pulse-glow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
