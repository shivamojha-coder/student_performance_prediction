export default {
  content: ["./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(214 32% 91%)",
        input: "hsl(214 32% 91%)",
        ring: "hsl(189 85% 30%)",
        background: "hsl(42 33% 96%)",
        foreground: "hsl(210 18% 17%)",
        primary: {
          DEFAULT: "hsl(189 85% 30%)",
          foreground: "hsl(0 0% 100%)"
        },
        muted: {
          DEFAULT: "hsl(210 17% 95%)",
          foreground: "hsl(210 14% 41%)"
        },
        accent: {
          DEFAULT: "hsl(16 92% 64%)",
          foreground: "hsl(0 0% 100%)"
        },
        card: {
          DEFAULT: "hsla(0 0% 100% / 0.72)",
          foreground: "hsl(210 18% 17%)"
        }
      },
      boxShadow: {
        glow: "0 20px 50px rgba(16, 123, 124, 0.22)",
        soft: "0 14px 32px rgba(19, 31, 44, 0.12)"
      },
      backgroundImage: {
        "hero-radial": "radial-gradient(95rem 60rem at 95% -20%, rgba(15, 139, 141, 0.34), transparent 58%), radial-gradient(82rem 42rem at -20% 10%, rgba(255, 127, 80, 0.3), transparent 60%), radial-gradient(70rem 40rem at 50% 120%, rgba(56, 189, 248, 0.16), transparent 68%), linear-gradient(180deg, #f8f5ee 0%, #edf6fb 100%)"
      },
      keyframes: {
        "gradient-shift": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" }
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.65" },
          "50%": { opacity: "1" }
        }
      },
      animation: {
        "gradient-shift": "gradient-shift 3s ease infinite",
        pulseSoft: "pulseSoft 1.6s ease-in-out infinite"
      }
    }
  },
  corePlugins: {
    preflight: false
  },
  plugins: []
};
