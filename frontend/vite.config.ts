import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import { vercelPlugin } from "vite-plugin-vercel"
export default defineConfig({ 
  plugins: [react(), vercelPlugin({ 
    rewrites: [{ source: "/(.*)", destination: "/index.html" }] 
  })], 
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
