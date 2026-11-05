# Consistent Linux raster/vector runtime for Linux, macOS and Windows Docker hosts.
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libpotrace0 libcairo2 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/raster-2-vector
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY scripts ./scripts
COPY SKILL.md ./SKILL.md
ENTRYPOINT ["python","/opt/raster-2-vector/scripts/r2v.py"]
CMD ["doctor"]
