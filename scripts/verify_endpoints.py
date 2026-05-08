#!/usr/bin/env python3
"""Pinga websites e atualiza status."""
import asyncio, yaml
from pathlib import Path
import httpx
from rich.console import Console
from rich.progress import Progress

ROOT = Path(__file__).resolve().parent.parent
console = Console()

async def check(client, e):
    url = e.get("website") or e.get("github")
    if not url: return e["slug"], None
    try:
        r = await client.head(url, timeout=10, follow_redirects=True)
        return e["slug"], r.status_code < 500
    except Exception:
        try:
            r = await client.get(url, timeout=10, follow_redirects=True)
            return e["slug"], r.status_code < 500
        except Exception:
            return e["slug"], False

async def main():
    hub = yaml.safe_load((ROOT / "data/hub.yaml").read_text())
    results = {}
    async with httpx.AsyncClient(headers={"User-Agent": "FreeLLMHub/1.0"}) as client:
        with Progress() as progress:
            task = progress.add_task("Verificando...", total=len(hub))
            for batch_start in range(0, len(hub), 20):
                batch = hub[batch_start:batch_start+20]
                tasks = [check(client, e) for e in batch]
                for slug, ok in await asyncio.gather(*tasks):
                    results[slug] = ok
                    progress.advance(task)

    ok_count = sum(1 for v in results.values() if v)
    console.print(f"\n✅ {ok_count}/{len(hub)} endpoints respondendo")

    import json
    (ROOT / "data/verified.json").write_text(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
