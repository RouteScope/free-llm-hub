#!/usr/bin/env python3
"""Verifica se endpoints respondem (HEAD com fallback GET, retry, UA realista)."""
import asyncio
import json
from pathlib import Path
import httpx
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()
ROOT = Path(__file__).resolve().parent.parent

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
TIMEOUT = httpx.Timeout(15.0, connect=10.0)
CONCURRENCY = 20

# Considera estes status como "vivo" (sites que bloqueiam mas existem)
ALIVE_STATUSES = {200, 201, 202, 204, 301, 302, 303, 307, 308, 401, 403, 405, 429}


async def check(client, slug, url, sem):
    async with sem:
        for method in ("HEAD", "GET"):
            try:
                r = await client.request(method, url, follow_redirects=True, timeout=TIMEOUT)
                if r.status_code in ALIVE_STATUSES:
                    return slug, True, r.status_code
                # 4xx genérico ainda pode indicar site vivo
                if 200 <= r.status_code < 500 and r.status_code != 404:
                    return slug, True, r.status_code
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout):
                continue
            except Exception:
                continue
        return slug, False, 0


async def main():
    hub = yaml.safe_load((ROOT / "data/hub.yaml").read_text())
    targets = [(e["slug"], e.get("website") or e.get("github"))
               for e in hub if e.get("website") or e.get("github")]

    sem = asyncio.Semaphore(CONCURRENCY)
    results = {}
    statuses = {}

    async with httpx.AsyncClient(headers=HEADERS, http2=False, verify=True) as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Verificando..."),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("check", total=len(targets))
            tasks = [check(client, slug, url, sem) for slug, url in targets]
            for coro in asyncio.as_completed(tasks):
                slug, ok, code = await coro
                results[slug] = ok
                statuses[slug] = code
                progress.advance(task)

    (ROOT / "data/verified.json").write_text(json.dumps(results, indent=2))
    (ROOT / "data/verified_status.json").write_text(json.dumps(statuses, indent=2))

    alive = sum(1 for v in results.values() if v)
    total = len(results)
    pct = 100 * alive / total if total else 0
    console.print(f"\n[green]✅ {alive}/{total} endpoints respondendo ({pct:.1f}%)[/green]")

    down = [s for s, v in results.items() if not v]
    if down:
        console.print(f"[red]❌ {len(down)} fora do ar:[/red]")
        for d in down:
            console.print(f"  - {d}")


if __name__ == "__main__":
    asyncio.run(main())
