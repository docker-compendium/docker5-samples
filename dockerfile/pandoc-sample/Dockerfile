# Dockerfile
FROM ubuntu:24.04
RUN apt-get update -y && \
    apt-get install -y -o Acquire::Retries=10 \
                     --no-install-recommends \
      texlive-latex-recommended \
      texlive-latex-extra \
      texlive-fonts-recommended \
      texlive-lang-german \
      texlive-pstricks \
      texlive-fonts-extra \
      imagemagick \
      unzip \
      python3 \
      ghostscript \
      locales \
      joe \
      vim \
      curl \
      wget \
      ca-certificates \
      less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
ENV TZ="Europe/Berlin" 
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

# install a specific Pandoc version for amd64 or arm64 platform
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "amd64" ]; then \
      curl -L https://github.com/jgm/pandoc/releases/download/3.8.2.1/pandoc-3.8.2.1-1-amd64.deb \
        -o /tmp/pandoc.deb && \
      dpkg -i /tmp/pandoc.deb && \
      rm /tmp/pandoc.deb; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
      curl -L https://github.com/jgm/pandoc/releases/download/3.8.2.1/pandoc-3.8.2.1-1-arm64.deb \
        -o /tmp/pandoc.deb && \
      dpkg -i /tmp/pandoc.deb && \
      rm /tmp/pandoc.deb; \
    fi
   

# install fonts
# (unfortunately, we cannot provide the fonts file)
# ADD myfonts.tgz /usr/local/share/texmf
# RUN texhash 

# /data volume
# connect to your local directory with *.md files
# when executing docker run:
# - docker run -v "$(pwd)":/data 
VOLUME  ["/data"]

# start command
ENTRYPOINT ["/bin/bash"]
