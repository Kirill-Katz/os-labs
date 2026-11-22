FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive LC_ALL=C TZ=UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3 time \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work/lab11
CMD ["python3", "code/run.py"]
