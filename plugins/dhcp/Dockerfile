FROM debian:stable

EXPOSE 67/udp

RUN apt-get update \
 && apt-get install kea-dhcp4-server -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["kea-dhcp4"]
