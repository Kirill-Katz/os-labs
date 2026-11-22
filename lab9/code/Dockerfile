FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive LC_ALL=C TZ=UTC
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev make strace python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
CMD ["sh", "code/run.sh"]
