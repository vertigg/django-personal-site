/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["**/templates/**/*.{html,js}", "**/static/**/*.{html,js}", "**/forms.py", "**/filters.py"],
  blocklist: [
    'collapse', // until we deal with collapsable nav
  ],
  theme: {
    extend: {
      fontFamily: {
        'gotham': ['Gotham-Book', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
        'fontin': ['Fontin-Regular', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
