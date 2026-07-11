// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build
export default defineConfig({
  site: 'https://ilaicollective.com',
  server: {
    port: Number(process.env.PORT) || 4321,
    host: true,
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
