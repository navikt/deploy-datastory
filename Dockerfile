FROM gcr.io/distroless/cc AS cc
FROM europe-north1-docker.pkg.dev/cgr-nav/pull-through/nav.no/python:3.14-dev AS dev

USER root
RUN apk add --update jq curl shadow fontconfig wget

# Install XKCD font (the actual "xkcd" font, not "xkcd Script")
RUN wget -O /tmp/xkcd.otf "https://github.com/ipython/xkcd-font/raw/master/xkcd/build/xkcd.otf" && \
    wget -O /tmp/xkcd-Regular.otf "https://github.com/ipython/xkcd-font/raw/master/xkcd/build/xkcd-Regular.otf" && \
    mkdir -p /usr/share/fonts/truetype/xkcd && \
    mv /tmp/xkcd.otf /usr/share/fonts/truetype/xkcd/ && \
    mv /tmp/xkcd-Regular.otf /usr/share/fonts/truetype/xkcd/ && \
    fc-cache -fv

WORKDIR /quarto

RUN useradd -m -d /quarto/ -u 1069 -s /bin/bash quarto && \
    chown -R quarto:quarto /quarto/

RUN QUARTO_VERSION=$(curl https://api.github.com/repos/quarto-dev/quarto-cli/releases/latest | jq '.tag_name' | sed -e 's/[\"v]//g') && \
    wget https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz && \
    tar -xvzf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz && \
    mv quarto-${QUARTO_VERSION}/bin/* /usr/local/bin && \
    mv quarto-${QUARTO_VERSION}/share /usr/local/share/ && \
    rm -rf quarto-${QUARTO_VERSION}-linux-amd64.tar.gz

USER quarto

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=quarto:quarto main.py .
COPY --chown=quarto:quarto deploy-complete-doc-datafortelling.ipynb .

ENTRYPOINT ["python", "main.py"]