import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        tropmed: {
          primary: "#0d9488",   // teal-600
          neutral: "#64748b",   // slate-500
          danger: "#dc2626",    // red-600
          warning: "#d97706",   // amber-600
        },
      },
    },
  },
  plugins: [],
};

export default config;
