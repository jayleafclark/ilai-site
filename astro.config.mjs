// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build
// Preview build serves at github.io/ilai-site (subpath). Set BASE=/ for the
// custom-domain (root) launch build.
export default defineConfig({
  site: 'https://ilaicollective.com',
  base: process.env.BASE ?? '/ilai-site',
  server: {
    port: Number(process.env.PORT) || 4321,
    host: true,
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
