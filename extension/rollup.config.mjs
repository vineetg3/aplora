/**
 * @license
 * Copyright 2024 Google Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
import {nodeResolve} from '@rollup/plugin-node-resolve';

export default {
  input: ["popup.js", "background.js","content.js"],
  output: {
    format: "esm",
    dir: "out",
    entryFileNames: "[name].js", // Preserve input filenames in output
    chunkFileNames: "[name]-[hash].js", // Shared chunks for common dependencies
  },
  // If you do not need to use WebDriver BiDi protocol,
  // exclude chromium-bidi/lib/cjs/bidiMapper/BidiMapper.js to minimize the bundle size.
  external: ["chromium-bidi/lib/cjs/bidiMapper/BidiMapper.js"],
  plugins: [
    nodeResolve({
      browser: true,
      resolveOnly: ["puppeteer-core"],
    }),
  ],
};
