FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y python3 python3-pip build-essential libssl-dev libffi-dev

WORKDIR /app
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "mnemonic_bruteforce_multiproces.py"]
