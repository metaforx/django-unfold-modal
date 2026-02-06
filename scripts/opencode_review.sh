#!/usr/bin/env bash
set -euo pipefail

MODEL="${MODEL:-kimi-k2.5}"
INPUT="$(cat)"

PROMPT=$'You are a strict senior code reviewer.\nReview the following content. Be concise, actionable, and critical.\n'

tmpfile="$(mktemp)"
printf '%s\n\n%s\n' "$PROMPT" "$INPUT" > "$tmpfile"

opencode run --model "$MODEL" --prompt-file "$tmpfile"

rm -f "$tmpfile"
