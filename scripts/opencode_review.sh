#!/usr/bin/env bash
set -euo pipefail

MODEL="${MODEL:-opencode/kimi-k2.5-free}"
INPUT="$(cat)"

PROMPT='You are a strict senior code reviewer. Review the following content. Be concise, actionable, and critical.'

opencode run --model "$MODEL" "$PROMPT

$INPUT"
