#!/usr/bin/env python3
"""Adiciona websites oficiais que estavam faltando, usando ruamel.yaml (preserva ordem/comentários)."""
from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO

ROOT = Path(__file__).resolve().parent.parent

WEBSITES = {
    # Inference Engines
    "llama-cpp": "https://github.com/ggml-org/llama.cpp",
    "tgi": "https://huggingface.co/docs/text-generation-inference",
    "sglang": "https://sgl-project.github.io",
    "tensorrt-llm": "https://nvidia.github.io/TensorRT-LLM",
    "lmdeploy": "https://lmdeploy.readthedocs.io",
    "mlc-llm": "https://llm.mlc.ai",
    "ktransformers": "https://kvcache-ai.github.io/ktransformers",
    "exllamav2": "https://github.com/turboderp-org/exllamav2",
    "aphrodite": "https://aphrodite.pygmalion.chat",
    "ctranslate2": "https://opennmt.net/CTranslate2",
    # Desktop UIs
    "text-gen-webui": "https://github.com/oobabooga/text-generation-webui",
    "koboldcpp": "https://github.com/LostRuins/koboldcpp",
    # Gateways
    "one-api": "https://github.com/songquanpeng/one-api",
    "new-api": "https://github.com/Calcium-Ion/new-api",
    "routellm": "https://lmsys.org/blog/2024-07-01-routellm",
    "phoenix": "https://docs.arize.com/phoenix",
    # Frameworks
    "autogen": "https://microsoft.github.io/autogen",
    "langgraph": "https://langchain-ai.github.io/langgraph",
    "pydantic-ai": "https://ai.pydantic.dev",
    "dspy": "https://dspy.ai",
    "semantic-kernel": "https://learn.microsoft.com/semantic-kernel",
    "vercel-ai-sdk": "https://sdk.vercel.ai",
    # Coding tools
    "cline": "https://cline.bot",
    "openhands": "https://www.all-hands.dev",
    "codex-cli": "https://github.com/openai/codex",
    # Specialty
    "coqui-tts": "https://github.com/coqui-ai/TTS",
    "kokoro": "https://github.com/hexgrad/kokoro",
    "whisper": "https://openai.com/research/whisper",
    "faster-whisper": "https://github.com/SYSTRAN/faster-whisper",
    "comfyui": "https://www.comfy.org",
    "a1111-webui": "https://github.com/AUTOMATIC1111/stable-diffusion-webui",
    # Vector DBs
    "pgvector": "https://github.com/pgvector/pgvector",
    "lancedb": "https://lancedb.com",
    "vespa": "https://vespa.ai",
    # Eval
    "promptfoo": "https://promptfoo.dev",
    "deepeval": "https://deepeval.com",
    "ragas": "https://ragas.io",
    "openai-evals": "https://github.com/openai/evals",
    # Open-weights families
    "llama-family": "https://llama.com",
    "qwen-family": "https://qwenlm.github.io",
    "deepseek-family": "https://www.deepseek.com",
    "mistral-family": "https://mistral.ai",
    "gemma-family": "https://ai.google.dev/gemma",
    "phi-family": "https://huggingface.co/microsoft/phi-4",
    "yi-family": "https://01.ai",
    "internlm-family": "https://internlm.intern-ai.org.cn",
    "glm-family": "https://github.com/THUDM/GLM-4",
    "hermes-family": "https://nousresearch.com",
    "gpt-oss": "https://openai.com/index/introducing-gpt-oss",
    "granite-family": "https://www.ibm.com/granite",
    "olmo-family": "https://allenai.org/olmo",
    "smollm": "https://huggingface.co/blog/smollm",
}

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=2, offset=0)


def reorder_entry(entry):
    """Reordena chaves para que slug, name, category, website, github fiquem no topo."""
    preferred_order = [
        "slug", "name", "category", "subcategory", "country",
        "website", "github", "license", "open_source", "openai_compatible",
        "pricing", "rate_limits", "models", "tags", "notes",
        "sources", "last_verified", "status",
    ]
    new_entry = type(entry)()  # mantém o tipo (CommentedMap)
    for key in preferred_order:
        if key in entry:
            new_entry[key] = entry[key]
    # Adiciona chaves que não estão na lista preferida
    for key in entry:
        if key not in new_entry:
            new_entry[key] = entry[key]
    return new_entry


def fix_file(path: Path):
    with path.open() as f:
        data = yaml.load(f)

    if data is None:
        return 0

    fixed_count = 0
    for i, entry in enumerate(data):
        slug = entry.get("slug")
        if not slug:
            continue
        if "website" not in entry and "github" not in entry and slug in WEBSITES:
            entry["website"] = WEBSITES[slug]
            data[i] = reorder_entry(entry)
            fixed_count += 1
        elif "website" not in entry and slug in WEBSITES:
            # Tem github mas não tem website - adicionamos só se quisermos canonicalizar
            # Pulamos para não alterar entradas funcionais
            pass

    if fixed_count > 0:
        with path.open("w") as f:
            yaml.dump(data, f)

    return fixed_count


def main():
    total = 0
    for f in sorted((ROOT / "data").glob("0*.yaml")):
        n = fix_file(f)
        if n:
            print(f"✏️  {f.name}: +{n} website(s)")
            total += n
    print(f"\n✅ {total} entrada(s) corrigida(s) no total")
    if total == 0:
        # Diagnóstico
        print("\n🔎 Diagnóstico — entradas sem website nem github:")
        import yaml as pyyaml
        hub_path = ROOT / "data" / "hub.yaml"
        if hub_path.exists():
            hub = pyyaml.safe_load(hub_path.read_text())
            missing = [e["slug"] for e in hub if not e.get("website") and not e.get("github")]
            for m in missing:
                in_dict = "✓ está em WEBSITES" if m in WEBSITES else "✗ FALTA no dict WEBSITES"
                print(f"  - {m}: {in_dict}")


if __name__ == "__main__":
    main()
