import { defineConfig } from 'vite';

const offline = process.env.COURSE_BASE === './';

export default defineConfig({
  base: process.env.COURSE_BASE ?? '/ai_bme_intro/',
  build: offline ? {
    modulePreload: false,
    rollupOptions: {
      output: {
        format: 'es',
        inlineDynamicImports: true,
        entryFileNames: 'assets/app.js',
      },
    },
  } : undefined,
});
