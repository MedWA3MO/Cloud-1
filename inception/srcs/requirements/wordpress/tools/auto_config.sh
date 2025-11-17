#!/bin/bash

sleep 20

echo "listen = wordpress:9000" >> /etc/php/7.4/fpm/pool.d/www.conf

wp config create	--allow-root \
					--dbname=$SQL_DATABASE \
					--dbuser=$SQL_USER \
					--dbpass=$SQL_PASSWORD \
					--dbhost=$DB_HOST \
					--path=$WP_PATH \
|| echo "Error creating wp-config.php"

wp core install		--allow-root \
					--url=$DOMAIN_NAME \
					--title="The Website" \
					--admin_user=$WP_ADMINE \
					--admin_password=$WP_ADMINE_PASSWORD \
					--admin_email=$WP_ADMINE_EMAIL \
					--path=$WP_PATH \
|| echo "Error installing WordPress";

wp user create	$WP_USER $WP_USER_EMAIL \
				--allow-root \
				--role=$WP_ROLE \
				--user_pass=$WP_USER_PASSWORD \
				--path=$WP_PATH \
|| echo "Error creating test user"

/usr/sbin/php-fpm7.4 -F || echo "Error starting PHP-FPM"