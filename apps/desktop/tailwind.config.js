/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/renderer/**/*.{html,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#0f0f12",
        panel: "#17171c",
        accent: "#6366f1",
      },
    },
  },
  plugins: [],
};
