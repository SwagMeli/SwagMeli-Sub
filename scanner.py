import asyncio
import base64
import ssl
import socket
from typing import List, Optional

INPUT_FILE = "Trash/Test.txt"
OUTPUT_FILE = "main/final.txt"
CONCURRENT_LIMIT = 100
LATENCY_TIMEOUT = 5.0

def decode_vless(uri: str) -> Optional[tuple]:
    if not uri.startswith("vless://"):
        return None
    try:
        address, port = uri[8:].split("@")[1].split(":")
        return address, int(port)
    except (IndexError, ValueError):
        return None

def decode_vmess(uri: str) -> Optional[tuple]:
    if not uri.startswith("vmess://"):
        return None
    try:
        decoded = base64.urlsafe_b64decode(uri[8:] + "=").decode("utf-8")
        parts = {kv.split(":")[0]: kv.split(":")[1] for kv in decoded.strip().split(",")}
        return parts["add"], int(parts["port"])
    except (KeyError, ValueError, base64.binascii.Error):
        return None

def parse_uri(uri: str) -> Optional[tuple]:
    return decode_vless(uri) or decode_vmess(uri)

async def measure_latency(address: str, port: int) -> float:
    loop = asyncio.get_event_loop()
    ctx = ssl.create_default_context()
    
    try:
        start = loop.time()
        reader, writer = await asyncio.open_connection(address, port, ssl=ctx)
        writer.close()
        await writer.wait_closed()
        return loop.time() - start
    except Exception:
        return None

async def process_uri(sem: asyncio.Semaphore, uri: str, results: List[tuple]):
    async with sem:
        config = parse_uri(uri)
        if not config:
            return
        address, port = config
        latency = await measure_latency(address, port)
        if latency:
            print(f"Config [{address}:{port}]: {int(latency * 1000)}ms")
            results.append((uri, latency))

async def main():
    sem = asyncio.Semaphore(CONCURRENT_LIMIT)
    results = []

    with open(INPUT_FILE, "r") as f:
        uris = [line.strip() for line in f.readlines() if line.strip()]

    await asyncio.gather(*[process_uri(sem, uri, results) for uri in uris])

    # Sort by latency (fastest first) and save successful configs
    results.sort(key=lambda x: x[1])
    with open(OUTPUT_FILE, "w") as f:
        f.writelines(f"{uri}\n" for uri, _ in results)

if __name__ == "__main__":
    asyncio.run(main())