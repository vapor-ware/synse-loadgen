#
# BUILDER STAGE
#
FROM docker.io/vaporio/python:3.6 as builder

COPY requirements.txt .

RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location \
 && rm -rf /root/.cache

COPY . /synse-loadgen
RUN pip install --no-deps --prefix=/build --no-warn-script-location /synse-loadgen \
 && rm -rf /root/.cache

#
# RELEASE STAGE
#
FROM docker.io/vaporio/python:3.6-slim

LABEL maintainer="Vapor IO" \
      name="vaporio/synse-loadgen" \
      url="https://github.com/vapor-ware/synse-loadgen"

RUN groupadd -g 51453 synse \
 && useradd -u 51453 -g 51453 synse

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini curl \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /etc/synse-loadgen \
 && chown -R synse:synse /etc/synse-loadgen

COPY --from=builder /build /usr/local

USER synse
ENTRYPOINT ["/usr/bin/tini", "--", "synse_loadgen"]
