FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/node:24-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends docker.io && rm -rf /var/lib/apt/lists/*
WORKDIR /service
COPY sandbox/service.mjs sandbox/compare.mjs ./
EXPOSE 4311
CMD ["node", "service.mjs"]
