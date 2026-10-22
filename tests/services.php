<?php

declare(strict_types=1);

use Illuminate\Contracts\Console\Kernel;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Redis;

require '/var/www/html/vendor/autoload.php';
$app = require '/var/www/html/bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();
set_exception_handler(static function (Throwable $exception): never {
    fwrite(STDERR, "FAIL: ".$exception->getMessage()."\n");
    exit(1);
});

$check = static function (bool $ok, string $message): void {
    if (!$ok) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
    echo "PASS: {$message}\n";
};

$check(PHP_VERSION === '8.3.35', 'PHP is exactly 8.3.35');
foreach (['db', 'redis', 'mailpit'] as $host) {
    $check(gethostbyname($host) !== $host, "Service name resolves: {$host}");
}
$check(DB::connection()->getDatabaseName() === 'laravel_db', 'Laravel uses laravel_db');
$check(DB::selectOne('SELECT VERSION() AS version')->version === '8.0.39', 'MySQL is exactly 8.0.39');
$check(DB::table('users')->whereIn('email', ['alice@example.test', 'bob@example.test', 'carol@example.test'])->count() === 3, 'SQL initialized the three sample users');
$check(password_verify('password', DB::table('users')->where('email', 'alice@example.test')->value('password')), 'Sample password is stored as a working bcrypt hash');
try {
    DB::select('SELECT * FROM wp_db.wp_options LIMIT 1');
    throw new RuntimeException('Laravel DB account can read WordPress DB');
} catch (Illuminate\Database\QueryException $exception) {
    $check((int) $exception->errorInfo[1] === 1142, 'Laravel DB account cannot read WordPress DB');
}

$unauthenticated = new \Redis();
$unauthenticated->connect('redis', 6379, 3);
try {
    $unauthenticated->ping();
    throw new RuntimeException('Redis accepted an unauthenticated client');
} catch (RedisException $exception) {
    $check(str_contains($exception->getMessage(), 'NOAUTH'), 'Redis rejects unauthenticated clients');
} finally {
    $unauthenticated->close();
}
$check((bool) Redis::ping(), 'Laravel authenticates to Redis');
$check(Redis::info('server')['redis_version'] === '7.4.2', 'Redis is exactly 7.4.2');
$check(config('cache.default') === 'redis', 'Laravel cache uses Redis');
$check(config('session.driver') === 'redis', 'Laravel sessions use Redis');
$check(config('queue.default') === 'redis', 'Laravel queues use Redis');
$key = 'lab-smoke-'.bin2hex(random_bytes(6));
Cache::put($key, 'ok', 60);
$check(Cache::get($key) === 'ok', 'Laravel Redis cache writes and reads');
Cache::forget($key);
$session = $app->make('session')->driver();
$session->start();
$session->put($key, 'session-ok');
$session->save();
$sessionId = $session->getId();
$session->flush();
$session->setId($sessionId);
$session->start();
$check($session->get($key) === 'session-ok', 'Laravel Redis session survives save and reload');
$session->getHandler()->destroy($sessionId);
$jobId = Queue::pushRaw(json_encode(["lab" => "connectivity-check", "attempts" => 0, "id" => $key], JSON_THROW_ON_ERROR), $key);
$job = Queue::pop($key);
$check($job !== null && json_decode($job->getRawBody(), true, flags: JSON_THROW_ON_ERROR)['lab'] === 'connectivity-check', 'Laravel Redis queue pushes and pops');
$job->delete();

Mail::raw('Laravel SMTP connectivity check in the isolated lab.', static function ($message): void {
    $message->to('reviewer@example.test')->subject('PHP isolated lab: SMTP OK');
});
echo "PASS: Laravel sent PHP isolated lab: SMTP OK to Mailpit\n";
