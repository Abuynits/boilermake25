import type { Config } from "tailwindcss";
import forms from '@tailwindcss/forms';

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      maxWidth: {
        '2xl': '42rem',
      },
      animation: {
        'fade-in-top': 'fadeInTop 0.3s ease-out',
      },
      keyframes: {
        fadeInTop: {
          '0%': { opacity: '0', transform: 'translate(-50%, -1rem)' },
          '100%': { opacity: '1', transform: 'translate(-50%, 0)' },
        },
      },
    },
  },
  plugins: [
    forms,
  ],
} satisfies Config;
