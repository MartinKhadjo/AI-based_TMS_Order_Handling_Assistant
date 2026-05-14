/*
 * Copyright (c) 2026 Martin Khadjavian. All rights reserved.
 * Website: https://martinkhadjavian.com
 */

import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173
  }
});
