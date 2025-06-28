/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    screens: {
      xs: "475px",
      sm: "640px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px",
    },
    extend: {
      colors: {
        // Consensus Agent brand colors from style guide
        "primary-teal": "#00C9A7",
        "primary-cyan": "#00FFFF",
        "primary-blue": "#0057FF",
        "primary-azure": "#00BFFF",
        "primary-green": "#00FF88",
        "primary-light-blue": "#0077FF",
        "primary-purple": "#8B5CF6",
        "primary-yellow": "#F59E0B",
        "primary-coral": "#FF6B6B",
        "accent-light-blue": "#B0F6FF",
        "accent-cyan": "#00FFFF",
        "bg-dark": "#0D1B2A",
        "bg-dark-secondary": "#0B0F1A",
        "bg-light": "#F5F9FF",
        "bg-light-secondary": "#FFFFFF",
      },
      fontFamily: {
        sans: ["Inter", "Space Grotesk", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(0, 255, 255, 0.3)",
        "glow-sm": "0 0 10px rgba(0, 255, 255, 0.2)",
      },
    },
  },
  plugins: [],
};
