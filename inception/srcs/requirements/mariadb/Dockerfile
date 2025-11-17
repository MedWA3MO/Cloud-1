#mariadb

FROM debian:bullseye

RUN apt-get update -y && apt-get install -y --fix-missing mariadb-server

COPY tools/script.sh /

EXPOSE 3306

RUN chmod +x /script.sh

CMD [ "./script.sh" ]
