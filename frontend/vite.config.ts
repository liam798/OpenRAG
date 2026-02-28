import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "fs";
import { resolve } from "path";

export default defineConfig({
  plugins: [
    react(),
    {
      name: "skill-md-utf8",
      configureServer(server) {
        const skillHandler = (req: any, res: any, next: () => void) => {
          if (req.url === "/skill.md" || req.url?.startsWith("/skill.md?")) {
            const file = resolve(process.cwd(), "public/skill.md");
            const body = readFileSync(file, "utf-8");
            res.setHeader("Content-Type", "text/markdown; charset=utf-8");
            res.setHeader("Cache-Control", "public, max-age=0");
            res.end(body);
            return;
          }
          next();
        };
        server.middlewares.stack.unshift({ route: "", handle: skillHandler });
      },
    },
  ],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
