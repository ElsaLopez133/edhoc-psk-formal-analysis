FROM debian:12-slim

LABEL version="1.0" \
      description="EDHOC-PSK analysis container with ProVerif + Tamarin" \
      org.opencontainers.image.authors="Elsa Lopez Perez"

# ------------------------------------------------------
# Install system dependencies
# ------------------------------------------------------
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      m4 ocaml ocamlbuild ocaml-findlib graphviz libgraphviz-dev \
      pkg-config curl build-essential git camlp4-extra \
      libgmp-dev zlib1g-dev libgtk2.0-dev liblablgtk2-ocaml-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------
# Install ProVerif 
# ------------------------------------------------------
# Install ProVerif from source (CLI only)
RUN cd /opt && \
    curl -fsSL -O https://proverif.inria.fr/proverif2.05.tar.gz && \
    tar -xzf proverif2.05.tar.gz && \
    cd proverif2.05 && \
    ./build  && \
    ln -s "$(pwd)/proverif" /usr/local/bin/proverif

# ------------------------------------------------------
# Install Tamarin Prover (prebuilt release)
# ------------------------------------------------------
RUN cd /opt && \
    curl -LO https://github.com/tamarin-prover/tamarin-prover/releases/download/1.10.0/tamarin-prover-1.10.0-linux64-ubuntu.tar.gz && \
    tar -xzf tamarin-prover-1.10.0-linux64-ubuntu.tar.gz && \
    chmod +x tamarin-prover && \
    mv tamarin-prover /usr/local/bin/tamarin-prover
    # mv tamarin-prover-* tamarin-prover  && \
    # ln -s /opt/tamarin-prover/tamarin-prover /usr/local/bin/tamarin-prover


# ------------------------------------------------------
# PATH for good measure (not strictly needed due to symlinks)
# ------------------------------------------------------
ENV PATH="/opt/proverif:/opt/tamarin-prover:$PATH"

# ------------------------------------------------------
# Project working directory
# ------------------------------------------------------
RUN mkdir -p /opt/lake-edhoc-psk
WORKDIR /opt/lake-edhoc-psk

# Copy repository into container
COPY . .

# ------------------------------------------------------
# Entrypoint
# ------------------------------------------------------
COPY Docker/res/entrypoint.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

EXPOSE 3001
