#nginx

FROM debian:bullseye

RUN apt-get -y update && apt-get -y install --fix-missing nginx openssl 

# /C: Country: "Morocco"
# /L: Locality: "Khouribga"
# /O: Organization: "1337FIL".
# /OU: Organizational Unit: "IT".
# /CN: Common Name: "mtigunit.42.ma".

RUN openssl req -x509 -nodes -newkey rsa:2048 \
	-keyout /etc/ssl/private/selfsigned.key \
	-out /etc/ssl/certs/selfsigned.crt \
	-subj "/C=MO/L=KH/O=1337FIL/OU=IT/CN=mtigunit.42.ma"

COPY ./conf/default.conf /etc/nginx/sites-available/default

EXPOSE 443

CMD [ "nginx", "-g", "daemon off;" ]