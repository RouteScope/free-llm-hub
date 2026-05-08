#!/usr/bin/env python3
"""Valida hub.yaml contra schema.json."""
import json, sys
from pathlib import Path
import yaml
from jsonschema import Draft7Validator
from rich.console import Console
from rich.table import Table

console = Console()
ROOT = Path(__file__).resolve().parent.parent

def main():
    schema = json.loads((ROOT / "data/schema.json").read_text())
    hub = yaml.safe_load((ROOT / "data/hub.yaml").read_text())
    validator = Draft7Validator(schema)

    errors = 0
    warnings = 0
    seen_slugs = set()

    for i, entry in enumerate(hub):
        slug = entry.get("slug", f"#{i}")

        # Duplicates
        if slug in seen_slugs:
            console.print(f"[red]✗ Duplicate slug: {slug}[/red]")
            errors += 1
        seen_slugs.add(slug)

        # Schema validation
        for err in validator.iter_errors(entry):
            console.print(f"[red]✗ {slug}: {err.message}[/red]")
            errors += 1

        # Warnings (não bloqueiam)
        if not entry.get("website") and not entry.get("github"):
            console.print(f"[yellow]⚠ {slug}: sem website nem github[/yellow]")
            warnings += 1
        if entry.get("category") == "open-weights-family" and not entry.get("github") and not entry.get("website"):
            warnings += 1

    # Stats
    table = Table(title="📊 Hub Stats")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="green")
    counts = {}
    for e in hub:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
        table.add_row(cat, str(n))
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{len(hub)}[/bold]")
    console.print(table)

    # Pricing breakdown
    pricing_table = Table(title="💰 Pricing Models")
    pricing_table.add_column("Model", style="cyan")
    pricing_table.add_column("Count", justify="right", style="green")
    pricing_counts = {}
    for e in hub:
        m = (e.get("pricing") or {}).get("model", "unknown")
        pricing_counts[m] = pricing_counts.get(m, 0) + 1
    for m, n in sorted(pricing_counts.items(), key=lambda x: -x[1]):
        pricing_table.add_row(m, str(n))
    console.print(pricing_table)

    if errors:
        console.print(f"\n[red]❌ {errors} erro(s) | ⚠ {warnings} warning(s)[/red]")
        sys.exit(1)
    if warnings:
        console.print(f"\n[yellow]⚠ {warnings} warning(s) (não-bloqueante)[/yellow]")
    console.print("[green]✅ Tudo válido[/green]")

if __name__ == "__main__":
    main()
