FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive LC_ALL=C TZ=UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu \
    qemu-system-misc bc perl python3 python3-pexpect \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work/xv6-riscv
