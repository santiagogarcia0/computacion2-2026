import asyncio
import aiohttp
import time

URLS = [
    "https://google.com"
] * 20


async def descargar(session, url):
    async with session.get(url) as response:
        await response.read()


async def secuencial():

    async with aiohttp.ClientSession() as session:

        inicio = time.perf_counter()

        for url in URLS:

            await descargar(session, url)

        fin = time.perf_counter()

    return fin - inicio


async def concurrente():

    async with aiohttp.ClientSession() as session:

        inicio = time.perf_counter()

        tareas = [
            descargar(session, url)
            for url in URLS
        ]

        await asyncio.gather(*tareas)

        fin = time.perf_counter()

    return fin - inicio


async def main():

    t1 = await secuencial()
    t2 = await concurrente()

    print(f"Secuencial: {t1:.2f} segundos")
    print(f"Concurrente: {t2:.2f} segundos")
    print(f"Speedup: {t1/t2:.2f}x")


asyncio.run(main())