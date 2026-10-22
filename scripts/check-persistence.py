#!/usr/bin/env python3
"""検証用の印を作り、再起動・再作成後にも残ることを確認する。"""
import json
from pathlib import Path
import subprocess
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent


def compose(*args, input=None):
    return subprocess.check_output(['docker', 'compose', *args], input=input, text=True, cwd=ROOT)


def php(body):
    return compose('exec', '-T', '--user', 'www-data', 'app', 'php', input='''<?php
require 'vendor/autoload.php';
$app = require 'bootstrap/app.php';
$app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap();
set_exception_handler(static function (Throwable $exception): never {
    fwrite(STDERR, $exception->getMessage()); exit(1);
});
'''+body)


def messages():
    with urllib.request.urlopen('http://127.0.0.1:8025/api/v1/messages', timeout=10) as response:
        return {message['ID'] for message in json.load(response)['messages']}


def verify():
    assert php(f'''if (Illuminate\\Support\\Facades\\DB::table('users')->where('email', '{marker}@example.test')->count() !== 1) exit(1);
if (Illuminate\\Support\\Facades\\Redis::get('{marker}') !== 'retained') exit(1);
if (file_get_contents(storage_path('{marker}')) !== 'retained') exit(1);
''') == ''
    assert compose('exec', '-T', '--user', 'www-data', 'wordpress', 'cat', f'/var/www/html/.{marker}') == 'retained'
    assert before_messages <= messages(), 'Mailpit lost messages'


compose('up', '-d', '--wait', '--wait-timeout', '180')
marker = 'lab-persistence-'+uuid.uuid4().hex
before_messages = messages()
assert before_messages, 'Run scripts/check.sh first to send a message'
php(f'''Illuminate\\Support\\Facades\\DB::insert("INSERT INTO users (name, email, password) SELECT 'Persistence Probe', '{marker}@example.test', password FROM users LIMIT 1");
Illuminate\\Support\\Facades\\Redis::set('{marker}', 'retained');
file_put_contents(storage_path('{marker}'), 'retained');
''')
compose('exec', '-T', '--user', 'www-data', 'wordpress', 'php', '-r', f"file_put_contents('/var/www/html/.{marker}', 'retained');")

try:
    compose('restart')
    compose('up', '-d', '--wait', '--wait-timeout', '180')
    verify()
    print('PASS: MySQL, Redis, Laravel storage, WordPress files and Mailpit survive restart')
    compose('up', '-d', '--force-recreate', '--wait', '--wait-timeout', '180')
    verify()
    print('PASS: all five named volumes retain data after container recreation')
finally:
    # この実行で作った印だけを片付け、検証者のデータは変更しない。
    php(f'''Illuminate\\Support\\Facades\\DB::table('users')->where('email', '{marker}@example.test')->delete();
Illuminate\\Support\\Facades\\Redis::del('{marker}');
unlink(storage_path('{marker}'));
''')
    compose('exec', '-T', '--user', 'www-data', 'wordpress', 'rm', f'/var/www/html/.{marker}')
