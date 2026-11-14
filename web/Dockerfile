# Build context = repo root (needs outputs/ for figures and scripts/ for the chatbot index).
FROM node:24-slim AS deps
WORKDIR /repo/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund

FROM deps AS build
COPY web/ ./
COPY outputs/ /repo/outputs/
COPY scripts/ /repo/scripts/
RUN npm run build && npm prune --omit=dev

FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production HOST=0.0.0.0 PORT=4321 DATA_DIR=/data/web CACHE_DIR=/cache
COPY --from=build /repo/web/package.json ./
COPY --from=build /repo/web/node_modules ./node_modules
COPY --from=build /repo/web/dist ./dist
RUN mkdir -p /cache && chown node:node /cache
USER node
EXPOSE 4321
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD node -e "fetch('http://127.0.0.1:4321/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "dist/server/entry.mjs"]
