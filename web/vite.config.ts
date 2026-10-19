import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: {
    port: 5173,
    watch: {
      ignored: ['**/*.glb', '**/*.bak', '**/colliders.json'],
    },
  },
  build: {
    target: 'es2020',
  },
});
