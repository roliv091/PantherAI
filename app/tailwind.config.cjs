/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'go-blue': '#00274C',
        'go-blue-light': '#003A6B',
        'maize': '#FFCB05',
      }
    },
  },
  plugins: [],
}
