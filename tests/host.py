"""公開された入口と Docker の実際のネットワーク状態を検証する。"""
import json
import subprocess
import urllib.request


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True)


def read_url(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        assert response.status == 200, url
        return response.read().decode()


assert "Let's get started" in read_url('http://127.0.0.1:8080/')
print('PASS: Laravel welcome page returns HTTP 200')
assert 'WordPress' in read_url('http://127.0.0.1:8081/')
assert 'Error establishing a database connection' not in read_url('http://127.0.0.1:8081/')
print('PASS: WordPress initial setup responds without a DB error')
assert 'Mailpit' in read_url('http://127.0.0.1:8025/')
mail = json.loads(read_url('http://127.0.0.1:8025/api/v1/messages'))
assert any(message['Subject'] == 'PHP isolated lab: SMTP OK' for message in mail['messages'])
print('PASS: Mailpit stored the message sent through Laravel SMTP')

containers = json.loads(docker('inspect', *docker('compose', 'ps', '-q').split()))
expected_ports = {'gateway': {'8080/tcp': '8080', '8081/tcp': '8081', '8025/tcp': '8025'}}
assert len(containers) == 7
for container in containers:
    service = container['Config']['Labels']['com.docker.compose.service']
    networks = container['NetworkSettings']['Networks']
    inspected_networks = [json.loads(docker('network', 'inspect', name))[0] for name in networks]
    if service == 'gateway':
        assert len(networks) == 2, (service, networks)
        assert sum(network['Internal'] for network in inspected_networks) == 1
    else:
        assert len(networks) == 1, (service, networks)
        assert inspected_networks[0]['Internal'] is True, service
    actual = {}
    for port, bindings in (container['NetworkSettings']['Ports'] or {}).items():
        for binding in bindings or []:
            assert binding['HostIp'] == '127.0.0.1', (service, binding)
            actual[port] = binding['HostPort']
    assert actual == expected_ports.get(service, {}), (service, actual)
    if service in ('app', 'wordpress'):
        assert container['Config']['User'] == 'www-data', service
print('PASS: six services use only internal labnet; gateway publishes only the three loopback ports')

# 起動スクリプトが nginx の親・子から権限を手放したことを実プロセスで確認する。
status = docker('compose', 'exec', '-T', 'gateway', 'cat', '/proc/1/status')
assert 'CapEff:\t0000000000000000' in status
assert 'CapBnd:\t0000000000000000' in status
assert 'NoNewPrivs:\t1' in status
assert 'Uid:\t0\t0\t0\t0' not in status
rules = docker('compose', 'exec', '-T', 'gateway', 'iptables', '-S', 'OUTPUT')
assert '-P OUTPUT DROP' in rules
assert '--dport 80 -j ACCEPT' in rules
assert '--dport 8080 -j ACCEPT' in rules
assert '--dport 8025 -j ACCEPT' in rules
print('PASS: gateway denies other outbound traffic and nginx has no retained capabilities')
