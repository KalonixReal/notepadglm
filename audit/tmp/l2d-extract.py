#!/usr/bin/env python3
"""Extract ~N chars around each regex match in a big file (L2-D harness helper)."""
import re, sys
path = sys.argv[1]; pattern = sys.argv[2]; before = int(sys.argv[3]) if len(sys.argv)>3 else 200; after = int(sys.argv[4]) if len(sys.argv)>4 else 2500
data = open(path, encoding='utf-8', errors='replace').read()
for m in list(re.finditer(pattern, data))[:20]:
    s = max(0, m.start()-before); e = min(len(data), m.end()+after)
    print(f"=== match@{m.start()} ===")
    print(data[s:e])
    print()
