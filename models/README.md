# LLM Models

This directory holds GGUF model files for the LLM parser. Model files are gitignored (too large for version control).

## Recommended Model

**Qwen2.5-3B-Instruct (Q4_K_M)** — ~2GB, fast on Apple Silicon (~80-120 tok/s)

### Automated Download

```bash
python3 scripts/download_model.py
```

### Manual Download

Using `huggingface-cli`:
```bash
pip install huggingface-hub
huggingface-cli download Qwen/Qwen2.5-3B-Instruct-GGUF qwen2.5-3b-instruct-q4_k_m.gguf --local-dir models/
```

Using `curl`:
```bash
curl -L -o models/qwen2.5-3b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf
```

## Usage

```bash
python3 -m cli.main games/zork1/ --parser llm --model models/qwen2.5-3b-instruct-q4_k_m.gguf
```

## Alternative Models

If 3B proves insufficient, try **Phi-3.5-mini-instruct** (Q4_K_M, ~2.4GB):
```bash
huggingface-cli download microsoft/Phi-3.5-mini-instruct-gguf Phi-3.5-mini-instruct-Q4_K_M.gguf --local-dir models/
```
