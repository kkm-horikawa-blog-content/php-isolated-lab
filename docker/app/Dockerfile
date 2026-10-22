# PHP 8.3.35 の公式 FPM / Debian bookworm。マルチアーキテクチャの索引を固定。
FROM composer:2.8.12@sha256:5248900ab8b5f7f880c2d62180e40960cd87f60149ec9a1abfd62ac72a02577c AS composer
FROM php:8.3.35-fpm-bookworm@sha256:ca090064188589bba7d1a2106356b15975bcab3d9e40c5b7df45c6e732ee0962

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash curl default-mysql-client redis-tools unzip \
        libicu-dev libonig-dev libzip-dev \
    && docker-php-ext-install -j"$(nproc)" pdo_mysql mbstring intl zip bcmath opcache \
    && pecl install redis-6.2.0 \
    && docker-php-ext-enable redis \
    && sed -i '/^user =/d; /^group =/d' /usr/local/etc/php-fpm.d/www.conf \
    && usermod --shell /bin/bash www-data \
    && rm -rf /var/lib/apt/lists/*
COPY --from=composer /usr/bin/composer /usr/local/bin/composer
WORKDIR /var/www/html
COPY applications/laravel/ ./
RUN composer install --no-dev --prefer-dist --no-interaction --optimize-autoloader \
    && mkdir -p storage/framework/cache/data storage/framework/sessions storage/framework/views storage/logs bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache
COPY docker/app/www.conf /usr/local/etc/php-fpm.d/zz-lab.conf
USER www-data
EXPOSE 9000
CMD ["php-fpm", "-F"]
