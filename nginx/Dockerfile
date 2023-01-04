FROM nginx:1.21.4
WORKDIR /tmp
RUN set -ex \
 && export DEBIAN_FRONTEND=noninteractive \
 && apt-get update \
 && apt-get install -y nginx-extras