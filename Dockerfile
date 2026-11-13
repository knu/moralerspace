FROM docker.io/library/ubuntu:26.04

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt-get update && \
    apt-get install -y \
        fontforge \
        libharfbuzz-bin \
        parallel \
        ttfautohint \
        python-is-python3 \
        python3 \
        python3-fontforge \
        python3-pip \
        python3-venv

RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --use-pep517 -r requirements.txt

WORKDIR /workspace

CMD ["bash", "./make.sh"]
