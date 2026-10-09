import asyncio
import time

async def llamada_falsa() -> None:
    inicio = time.perf_counter()
    print(await llamada_falsa("investigador", 1))
    print(await llamada_falsa("analista", 1))
    print(await llamada_falsa("sintetizador", 1))
    print(await llamada_falsa("sintetizador", 1))
    print(f"secuencial:{time.perf_counter() - inicio: .1f}s")


async def en_paralelo() -> None:
    inicio = time.perf_counter()
    resultads = await asyncio.gather(
        llamada_falsa("investigador", 1),
        llamada_falsa("analista", 1)
        llamada_falsa("sintetizador", 1)
    )

    for r in resultados:
        print(r)
    print(f"Paralelo: {time.perf_counter() - inici: .1f}s")


asyncio.run(secuencial())
asyncio.run(en_paralelo())