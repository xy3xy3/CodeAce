FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/node:24-bookworm-slim AS build
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts
COPY . .
RUN pnpm build
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/node:24-bookworm-slim
WORKDIR /app
COPY --from=build /app/.output ./.output
USER node
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
