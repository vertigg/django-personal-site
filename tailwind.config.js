/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["**/templates/**/*.{html,js}", "**/static/**/*.{html,js}", "**/forms.py", "**/filters.py"],
  blocklist: [],
  theme: {
    extend: {
      backgroundImage: {
        'default-pattern': "url('../image/lel.png')"
      },
      colors: {
        silver: "#c0c0c0"
      },
      fontFamily: {
        'gotham': ['Gotham-Book', 'Arial'],
        'fontin': ['Fontin-Regular', 'Arial'],
      },
    },
  },
  plugins: [],
}
