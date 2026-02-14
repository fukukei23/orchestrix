/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#9333ea',
          100: '#805ad5',
          200: '#a78bfa',
          300: '#7c3aed',
          400: '#6366f1',
          500: '#4f46e5',
          600: '#3b82f6',
          700: '#2563eb',
          800: '#1d4ed8',
          900: '#1e3a8a',
        },
      }
    }
  },
  plugins: [
    require('tailwindcss-animate'),
  ]
}
