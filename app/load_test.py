import asyncio
import time
import aiohttp
import uuid

URL = "http://127.0.0.1:8000/reward/decide"
TOTAL_REQUESTS = 1000
CONCURRENCY = 50

async def send_request(session, i):
    payload = {
        "txn_id": f"txn_{i}",
        "user_id": "u2",
        "merchant_id": "amazon",
        "amount": 500,
        "txn_type": "CARD",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    start = time.time()
    async with session.post(URL, json=payload) as resp:
        await resp.json()
    return time.time() - start


async def run():
    timings = []
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(TOTAL_REQUESTS):
            tasks.append(send_request(session, i))

        start = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start

        timings.extend(results)

    timings.sort()
    p95 = timings[int(0.95 * len(timings))]
    p99 = timings[int(0.99 * len(timings))]
    rps = TOTAL_REQUESTS / total_time

    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests/sec: {rps:.2f}")
    print(f"P95 latency: {p95:.3f}s")
    print(f"P99 latency: {p99:.3f}s")


if __name__ == "__main__":
    asyncio.run(run())
