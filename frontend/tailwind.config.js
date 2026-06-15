/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--canvas)',
        'canvas-soft': 'var(--canvas-soft)',
        surface: 'var(--surface)',
        primary: 'var(--primary)',
        'primary-active': 'var(--primary-active)',
        ink: 'var(--ink)',
        'ink-secondary': 'var(--ink-secondary)',
        'ink-muted': 'var(--ink-muted)',
        'ink-faint': 'var(--ink-faint)',
        hairline: 'var(--hairline)',
        sticker: {
          sky: 'var(--sticker-sky)',
          purple: 'var(--sticker-purple)',
          'purple-deep': 'var(--sticker-purple-deep)',
          pink: 'var(--sticker-pink)',
          orange: 'var(--sticker-orange)',
          'orange-deep': 'var(--sticker-orange-deep)',
          teal: 'var(--sticker-teal)',
          green: 'var(--sticker-green)',
          brown: 'var(--sticker-brown)',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        xs: '4px',
        sm: '5px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        'notion-soft': 'rgba(0,0,0,0.01) 0 0.175px 1.041px, rgba(0,0,0,0.02) 0 0.8px 2.925px, rgba(0,0,0,0.027) 0 2.025px 7.847px, rgba(0,0,0,0.04) 0 4px 18px',
        'notion-elevated': 'rgba(0,0,0,0.05) 0 23px 52px',
      }
    },
  },
  plugins: [],
}
