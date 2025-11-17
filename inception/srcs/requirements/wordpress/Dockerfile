#wordpress

FROM debian:bullseye

RUN apt-get update && apt-get install -y --fix-missing wget php7.4 php-fpm php-mysql

RUN wget https://wordpress.org/latest.tar.gz -P /var/www
RUN cd /var/www && tar -xzf *.tar.gz && rm *.tar.gz

RUN wget https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
RUN chmod +x wp-cli.phar
RUN mv wp-cli.phar /usr/local/bin/wp

COPY tools/auto_config.sh /

WORKDIR /run/php/

EXPOSE 9000

RUN chmod +x /auto_config.sh

CMD [ "/auto_config.sh"]
