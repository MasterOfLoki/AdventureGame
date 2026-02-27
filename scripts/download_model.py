#!/usr/bin/env python3
"""Download the recommended LLM model for the adventure game parser."""

from __future__ import annotations

import os
import sys

REPO_ID = "Qwen/Qwen2.5-3B-Instruct-GGUF"
FILENAME = "qwen2.5-3b-instruct-q4_k_m.gguf"
LOCAL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")


def main() -> None:
    dest = os.path.join(LOCAL_DIR, FILENAME)
    if os.path.exists(dest):
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f"Model already exists: {dest} ({size_mb:.0f} MB)")
        return

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("huggingface-hub is required. Install with:")
        print("  pip install huggingface-hub")
        sys.exit(1)

    os.makedirs(LOCAL_DIR, exist_ok=True)

    print(f"Downloading {FILENAME} from {REPO_ID}...")
    print(f"Destination: {LOCAL_DIR}/")
    print("This is ~2GB and may take a few minutes.\n")

    path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        local_dir=LOCAL_DIR,
    )

    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"\nDone! Model saved to: {path} ({size_mb:.0f} MB)")
    print(f"\nTo play with LLM parser:")
    print(f"  python3 -m cli.main games/zork1/ --parser llm --model {path}")


if __name__ == "__main__":
    main()
