#!/usr/bin/env python3
"""Gera README.md mestre a partir de data/hub.yaml."""
from pathlib import Path
from collections import defaultdict
import yaml

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_NAMES = {
    "provider-api": "📡 Provider APIs",
    "inference-provider": "🔌 Inference Providers",
    "subscription-plan": "💰 Subscription Plans",
    "inference-engine": "🛠️ Inference Engines (OSS)",
    "gateway": "🚪 Gateways / Routers",
    "specialty-api": "🎨 Specialty APIs",
    "agent-framework": "🤖 Agent Frameworks",
    "llm-framework": "📚 LLM Frameworks",
    "vector-db": "🗄️ Vector Databases",
    "eval-framework": "📊 Eval Frameworks",
    "model-catalog": "📦 Model Catalogs",
    "coding-tool": "💻 Coding Tools",
    "desktop-ui": "🖥️ Desktop UIs",
    "open-weights-family": "🧬 Open-Weights Families",
}

def fmt_pricing(p):
    if not p: return "—"
    m = p.get("model", "")
    if m == "free": return "🟢 Free"
    if m == "freemium": return "🟢 Freemium"
    if m == "subscription":
        u = p.get("monthly_usd")
        return f"💳 ${u}/mo" if u else "💳 Custom"
    if m == "pay-per-token":
        i, o = p.get("input_per_mtok_usd"), p.get("output_per_mtok_usd")
        if i and o: return f"💵 ${i}/${o} per MTok"
        return "💵 Pay-per-token"
    if m == "trial-credits":
        c = p.get("trial_credits_usd")
        return f"🎁 ${c} trial" if c else "🎁 Trial"
    if m == "self-hosted": return "🏠 Self-hosted"
    return m

def fmt_limits(r):
    if not r: return "—"
    parts = []
    if r.get("rpm"): parts.append(f"{r['rpm']} RPM")
    if r.get("rpd"): parts.append(f"{r['rpd']} RPD")
    if r.get("tpm"): parts.append(f"{r['tpm']} TPM")
    if r.get("monthly_tokens"):
        mt = r["monthly_tokens"]
        parts.append(f"{mt:,} tok/mo")
    return ", ".join(parts) if parts else "—"

def main():
    hub = yaml.safe_load((ROOT / "data/hub.yaml").read_text())
    grouped = defaultdict(list)
    for e in hub:
        grouped[e["category"]].append(e)

    out = ["# 🌟 Free LLM Hub\n"]
    out.append("> A unified, community-driven catalog of LLM APIs, inference engines, gateways, and the entire OSS LLM ecosystem.\n")
    out.append(f"**Total entries:** {len(hub)} • **Last updated:** auto-generated\n")
    out.append("\n## 📑 Table of Contents\n")
    for cat in CATEGORY_NAMES:
        if cat in grouped:
            slug_anchor = CATEGORY_NAMES[cat].lower().replace(" ", "-").replace("/", "")
            out.append(f"- [{CATEGORY_NAMES[cat]}](#{slug_anchor}) ({len(grouped[cat])})")
    out.append("\n---\n")

    for cat, items in sorted(grouped.items(), key=lambda x: list(CATEGORY_NAMES).index(x[0]) if x[0] in CATEGORY_NAMES else 999):
        title = CATEGORY_NAMES.get(cat, cat)
        out.append(f"\n## {title}\n")

        # Subscription plans: ordena por preço
        if cat == "subscription-plan":
            items = sorted(items, key=lambda x: (x.get("pricing", {}) or {}).get("monthly_usd") or 999999)

        out.append("| Name | Country | Pricing | Rate Limits | Models / Notes | Link |")
        out.append("|------|:-:|:-:|:-:|------|:-:|")
        for e in items:
            name = e["name"]
            country = e.get("country", "—")
            pricing = fmt_pricing(e.get("pricing"))
            limits = fmt_limits(e.get("rate_limits"))
            models = ", ".join((e.get("models") or [])[:3]) or e.get("notes") or "—"
            if len(models) > 60: models = models[:57] + "..."
            link = f"[🔗]({e.get('website', e.get('github', '#'))})"
            out.append(f"| **{name}** | {country} | {pricing} | {limits} | {models} | {link} |")

    out.append("\n---\n")
    out.append("## 🤝 Contributing\n")
    out.append("Edit `data/0X-*.yaml`, run `./scripts/merge.sh && python scripts/render_readme.py`, open a PR.\n")
    out.append("## 📜 License\nMIT\n")

    (ROOT / "README.md").write_text("\n".join(out))
    print(f"✅ README.md gerado com {len(hub)} entradas")

if __name__ == "__main__":
    main()
