#!/bin/bash
# usage: srcctx.sh <grep-pattern> [before-bytes] [after-bytes]  — byte-offset context from notepad.html
P="$1"; B="${2:-300}"; A="${3:-900}"
F=/home/z/my-project/public/notepad.html
off=$(grep -obm1 -- "$P" "$F" | head -1 | cut -d: -f1)
if [ -z "$off" ]; then echo "NOT FOUND: $P"; exit 1; fi
echo "OFFSET: $off (byte in notepad.html)"
start=$((off - B)); [ $start -lt 0 ] && start=0
tail -c +$((start+1)) "$F" | head -c $((B + A))
echo
