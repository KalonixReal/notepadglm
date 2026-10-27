#!/bin/bash
# usage: l2b-src.sh <pattern>            — list byte offsets of ALL occurrences (up to 40) in notepad.html
#        l2b-src.sh <pattern> <occ#> [before] [after] — dump context around occurrence # (1-based)
P="$1"; F=/home/z/my-project/public/notepad.html
if [ -z "$P" ]; then echo "usage: l2b-src.sh <pattern> [occ#] [before=300] [after=900]"; exit 1; fi
if [ -z "$2" ]; then
  grep -ob -- "$P" "$F" | head -40 | cut -d: -f1 | tr '\n' ' '; echo
  exit 0
fi
N="$2"; B="${3:-300}"; A="${4:-900}"
off=$(grep -ob -- "$P" "$F" | sed -n "${N}p" | cut -d: -f1)
if [ -z "$off" ]; then echo "OCCURRENCE $N NOT FOUND (pattern: $P)"; exit 1; fi
echo "OCC#$N OFFSET: $off"
start=$((off - B)); [ $start -lt 0 ] && start=0
tail -c +$((start+1)) "$F" | head -c $((B + A))
echo
