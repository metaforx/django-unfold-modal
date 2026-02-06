#!/usr/bin/env bash
set -euo pipefail

MODEL="${MODEL:-opencode/kimi-k2.5-free}"
INPUT="$(cat)"

PROMPT=$'You are a senior engineer. Implement the requested changes.\nKeep edits minimal and follow existing conventions.\nReturn a concise plan first, then the patch or file edits.\n'

opencode run --model "$MODEL" --prompt "$PROMPT$INPUT"
