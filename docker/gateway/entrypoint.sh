#!/bin/sh
set -eu
# 途中で失敗すれば待受けを開始しない。ホストの通信規則は変更しない。
iptables -P OUTPUT DROP
iptables -F OUTPUT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -d 127.0.0.1/32 -o lo -j ACCEPT
iptables -A OUTPUT -d "$LAB_NGINX_IP/32" -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -d "$LAB_WORDPRESS_IP/32" -p tcp --dport 8080 -j ACCEPT
iptables -A OUTPUT -d "$LAB_MAILPIT_IP/32" -p tcp --dport 8025 -j ACCEPT
# 許可先の名前は extra_hosts で解決し、外部 DNS も問い合わせない。
# nginx の親・子にはネットワーク設定を変える権限を一切引き継がない。
exec setpriv --reuid=nginx --regid=nginx --init-groups \
    --bounding-set=-all --inh-caps=-all --ambient-caps=-all --no-new-privs \
    nginx -e stderr -g 'daemon off;'
