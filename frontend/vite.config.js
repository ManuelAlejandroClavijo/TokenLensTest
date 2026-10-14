import { defineConfig } from "vite";
export default defineConfig({
  base: "/",
  build: { outDir: "static", emptyOutDir: true },
  server: {
    host: "0.0.0.0",
    allowedHosts: true,
    proxy: { "/api": "http://127.0.0.1:4318" },
  },
});
