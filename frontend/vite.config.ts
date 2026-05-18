import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    hmr: {
      host: '127.0.0.1',
      port: 5173,
    },
  },

  build: {
    // Ensure fresh builds with no aggressive caching
    sourcemap: true,
  },
});


