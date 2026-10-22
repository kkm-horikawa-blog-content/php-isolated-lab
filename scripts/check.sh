#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
docker compose config --quiet
docker compose up -d --wait --wait-timeout 180

for service in app wordpress gateway; do
    if [[ "$service" != gateway ]]; then
        docker compose exec -T --user www-data "$service" bash -lc 'set -e; test "$(id -un)" = www-data; echo "PASS: www-data bash access"'
        docker compose exec -T --user www-data "$service" php -r 'exit(PHP_MAJOR_VERSION === 8 && PHP_MINOR_VERSION === 3 ? 0 : 1);'
    fi
    # 同じ curl で内部の正常応答が得られることを先に確かめる。
    docker compose exec -T --user www-data "$service" curl --fail --silent --max-time 5 http://nginx/up >/dev/null
    # IP 直指定でも、DNS を使った接続でも、外部へ出られないことを確かめる。
    if docker compose exec -T --user www-data "$service" curl --insecure --noproxy '*' --silent --connect-timeout 2 --max-time 3 https://1.1.1.1 >/dev/null 2>&1; then
        echo "FAIL: $service reached the external network" >&2
        exit 1
    fi
    if docker compose exec -T --user www-data "$service" curl --insecure --noproxy '*' --silent --connect-timeout 2 --max-time 3 https://example.com >/dev/null 2>&1; then
        echo "FAIL: $service reached an external hostname" >&2
        exit 1
    fi
    echo "PASS: $service cannot connect outside labnet"
done

docker compose exec -T --user www-data app bash -lc 'command -v mysql >/dev/null && command -v redis-cli >/dev/null && echo "PASS: mysql and redis-cli available"'
docker compose exec -T --user www-data app php < tests/services.php

python3 tests/host.py
