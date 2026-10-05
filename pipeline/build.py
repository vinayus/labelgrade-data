"""Build per-country packs from Open Food Facts + USDA.

  python -m pipeline.build --off off.csv.gz --usda usda.zip --out out/

Writes out/<country>.ndjson.gz (one record per line, see clean.py for keys),
out/index.json (counts, sizes, checksums) and out/stats.json.
"""
import argparse
import gzip
import hashlib
import json
import os
import time
from collections import Counter

from .clean import sane, merge
from .sources import read_off, read_usda

MIN_PACK = 50  # countries with fewer usable products go into 'world' only


def build(off_path, usda_path, out):
    os.makedirs(out, exist_ok=True)
    by_code = {}
    seen = Counter()
    for name, reader, path in (('off', read_off, off_path), ('usda', read_usda, usda_path)):
        if not path:
            continue
        for r in reader(path):
            seen[f'{name}_rows'] += 1
            if not sane(r):
                continue
            seen[f'{name}_usable'] += 1
            prev = by_code.get(r['b'])
            by_code[r['b']] = merge(prev, r) if prev else r
            if prev:
                seen['merged_across_sources'] += 1 if set(prev['src']) != set(r['src']) else 0
        print(f'{name}: {seen[name + "_rows"]:,} rows, {seen[name + "_usable"]:,} usable', flush=True)

    counts = Counter(c for r in by_code.values() for c in r['cc'])
    packs = {c for c, n in counts.items() if n >= MIN_PACK and c not in ('', 'world', 'unknown')}
    files = {c: gzip.open(os.path.join(out, f'{c}.ndjson.gz'), 'wt', encoding='utf-8') for c in packs | {'world'}}
    for r in by_code.values():
        line = json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n'
        homes = [c for c in r['cc'] if c in packs] or ['world']
        for c in homes:
            files[c].write(line)
    for f in files.values():
        f.close()

    index = {}
    for c in sorted(files):
        p = os.path.join(out, f'{c}.ndjson.gz')
        data = open(p, 'rb').read()
        index[c] = {'file': f'{c}.ndjson.gz', 'products': counts.get(c, 0) if c != 'world' else None,
                    'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    meta = {'built': time.strftime('%Y-%m-%d'), 'products': len(by_code), 'packs': index,
            'sources': {'off': 'Open Food Facts (ODbL) https://world.openfoodfacts.org',
                        'usda': 'USDA FoodData Central, branded foods (public domain) https://fdc.nal.usda.gov'}}
    json.dump(meta, open(os.path.join(out, 'index.json'), 'w'), indent=1)
    json.dump(dict(seen), open(os.path.join(out, 'stats.json'), 'w'), indent=1)
    print(f'{len(by_code):,} products in {len(files)} packs -> {out}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--off')
    ap.add_argument('--usda')
    ap.add_argument('--out', default='out')
    a = ap.parse_args()
    build(a.off, a.usda, a.out)
