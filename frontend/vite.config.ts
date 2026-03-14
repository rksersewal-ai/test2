// =============================================================================
// FILE: frontend/vite.config.ts
// Port assignments:
//   Frontend (Vite dev)  : 4173  — Vite's own preview port, safe on office PCs
//   Backend (Django)     : 8765  — avoids 8000 (DSC Signer), 8080 (proxies), 3000
// =============================================================================
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',       // accessible from LAN clients
    port: 4173,
    strictPort: true,      // fail fast if 4173 is taken
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
    strictPort: true,
  },
  build: {
    outDir: '../static/frontend',
    emptyOutDir: true,
  },
});
