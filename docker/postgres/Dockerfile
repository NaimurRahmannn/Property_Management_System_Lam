FROM postgis/postgis:16-3.5

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ca-certificates \
    postgresql-server-dev-16 \
    && git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install \
    && rm -rf /tmp/pgvector \
    && apt-get remove -y build-essential git postgresql-server-dev-16 \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY init/01-extensions.sql /docker-entrypoint-initdb.d/01-extensions.sql