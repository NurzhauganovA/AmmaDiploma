FROM python:3.11

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV TZ=Asia/Almaty

WORKDIR /app

RUN apt-get update && apt-get install -y \
    cmake \
    libgl1-mesa-glx

RUN pip install --upgrade pip

COPY /backend/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

COPY ./docker/dev/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]