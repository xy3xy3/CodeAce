FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends g++ time && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY sandbox/runner.py /opt/codeace/runner.py
USER 65534:65534
ENV OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /work
ENTRYPOINT ["python3", "/opt/codeace/runner.py"]
