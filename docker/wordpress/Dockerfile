# 公式 WordPress / Apache + mod_php / PHP 8.3 の取得済み索引を固定。
FROM wordpress:6.8.3-php8.3-apache@sha256:30bff39330d1693b0ce13d32fc9b7bb67193064f040b7d60d3494e136fa599d4
# root を使わず Apache 自体を動かすため、コンテナ内も非特権ポートにする。
RUN usermod --shell /bin/bash www-data \
    && sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf \
    && sed -i 's/:80>/:8080>/' /etc/apache2/sites-available/000-default.conf \
    && mkdir -p /var/run/apache2 /var/lock/apache2 \
    && chown -R www-data:www-data /var/run/apache2 /var/lock/apache2 /var/www/html
USER www-data
EXPOSE 8080
