import asyncio
import aiohttp
import time


async def download_url(session, url):
    """
    Descarga una URL individual.

    Devuelve:
    - status code
    - tamaño
    - tiempo
    """

    start = time.perf_counter()

    try:

        async with session.get(url) as response:

            content = await response.read()

            elapsed = time.perf_counter() - start

            return {
                "url": url,
                "status": response.status,
                "size": len(content),
                "time": round(elapsed, 3)
            }

    except Exception as e:

        return {
            "url": url,
            "error": str(e)
        }


async def execute_download_task(payload):

    urls = payload["urls"]

    async with aiohttp.ClientSession() as session:

        tasks = [
            download_url(session, url)
            for url in urls
        ]

        """
        asyncio.gather ejecuta TODAS
        concurrentemente.
        """

        results = await asyncio.gather(*tasks)

    return results