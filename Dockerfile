FROM python:3.13 AS compile-image

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .

RUN apt-get update && apt-get install -yq --no-install-recommends \
curl \
jq && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

RUN QUARTO_VERSION=1.8.25 && \
wget https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz && \
tar -xvzf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz && \
ln -s quarto-${QUARTO_VERSION} quarto-dist && \
rm -rf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz

RUN pip3 install --no-cache-dir -r requirements.txt

FROM python:3.13.7-slim AS runner-image

RUN apt-get update && apt-get install -yq --no-install-recommends \
    fontconfig \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install XKCD font
RUN wget -O /tmp/xkcd-script.ttf "https://github.com/ipython/xkcd-font/raw/master/xkcd-script/font/xkcd-script.ttf" && \
    mkdir -p /usr/share/fonts/truetype/xkcd && \
    mv /tmp/xkcd-script.ttf /usr/share/fonts/truetype/xkcd/ && \
    fc-cache -fv

RUN groupadd -g 1069 python && \
    useradd -r -u 1069 -g python python

WORKDIR /quarto
COPY --chown=python:python --from=compile-image /opt/venv /opt/venv
COPY --chown=python:python --from=compile-image quarto-dist/ quarto-dist/
RUN ln -s /quarto/quarto-dist/bin/quarto /usr/local/bin/quarto

ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m venv /opt/venv

COPY update_datastory.py .
COPY deploy-complete-doc-datafortelling.ipynb .

RUN chown python:python /quarto -R

ENV DENO_DIR=/quarto/deno
ENV XDG_CACHE_HOME=/quarto/cache
ENV XDG_DATA_HOME=/quarto/share

USER 1069
ENTRYPOINT ["python", "update_datastory.py"]