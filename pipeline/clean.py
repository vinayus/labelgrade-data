"""Turning messy source rows into one compact record shape, and throwing out what's broken.

Record keys are short on purpose (packs get downloaded by every user):
  b barcode, n name, br brand, q quantity, e energy kJ/100g, f fat, sf saturated fat,
  c carbs, s sugars, sa salt, fi fibre, p protein (all g/100g), i ingredients,
  src sources, cc countries
"""
import math
import re
import unicodedata

CORE = ('e', 's', 'sf', 'sa')


def normalize_barcode(raw):
    d = re.sub(r'\D', '', str(raw or ''))
    if len(d) == 14 and d.startswith('0'):
        d = d[1:]            # GTIN-14 with a packaging zero up front
    if 9 <= len(d) <= 12:
        d = d.zfill(13)      # UPC-A (and UPCs that lost leading zeros) -> EAN-13 so US and EU codes line up
    elif 6 <= len(d) <= 7:
        d = d.zfill(8)       # EAN-8 that lost its leading zero
    if len(d) not in (8, 13) or not d.strip('0'):
        return None
    return d


def num(v):
    try:
        x = float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return None
    if math.isnan(x) or x < 0:
        return None
    return x


def looks_like_ingredients(s):
    # same idea as src/core/match.js in the extension: OCR junk / addresses aren't ingredients
    t = str(s or '')
    if t.count(',') < 2:
        return False
    if re.search(r'\d{5,}|\d{3,}\s\d{3,}', t):
        return False
    chars = re.sub(r'\s', '', t)
    letters = sum(ch.isalpha() for ch in chars)
    return bool(chars) and letters / len(chars) > 0.75


def country_slug(name):
    s = str(name or '').strip().lower()
    s = s.split(':', 1)[1] if re.match(r'^[a-z]{2}:', s) else s
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def record(*, barcode, name, brand, quantity, energy_kj, fat, sat_fat, carbs, sugars, salt, fiber, protein,
           ingredients, source, countries):
    r = {
        'b': normalize_barcode(barcode), 'n': (name or '').strip()[:140], 'br': (brand or '').strip()[:80],
        'q': (quantity or '').strip()[:40], 'e': energy_kj, 'f': fat, 'sf': sat_fat, 'c': carbs, 's': sugars,
        'sa': salt, 'fi': fiber, 'p': protein, 'i': (ingredients or '').strip()[:2000],
        'src': [source], 'cc': sorted({c for c in countries if c}),
    }
    return r


def sane(r):
    """Keep only records the grader can actually use, with values that can all be true at once."""
    if not r.get('b') or not r.get('n'):
        return False
    if any(r.get(k) is None for k in CORE):
        return False
    if r['e'] > 3800:                         # pure fat is ~3700 kJ/100 g
        return False
    for k in ('f', 'sf', 'c', 's', 'sa', 'fi', 'p'):
        if r.get(k) is not None and r[k] > 100:
            return False
    if r.get('f') is not None and r['sf'] > r['f'] + 0.05:
        return False
    if r.get('c') is not None and r['s'] > r['c'] + 0.05:
        return False
    if r['i'] and not looks_like_ingredients(r['i']):
        r['i'] = ''                           # bad ingredient text: drop the text, keep the label
    return True


def merge(a, b):
    """Same barcode twice. USDA is manufacturer-submitted, so its numbers beat Open Food Facts;
    within one source the newer row wins. Gaps get filled from the other record."""
    if set(a['src']) == set(b['src']):
        first, second = b, a          # same source listed twice: the later (newer) row wins
    elif 'usda' in b['src'] and 'usda' not in a['src']:
        first, second = b, a
    else:
        first, second = a, b
    m = dict(first)
    for k, v in second.items():
        if k in ('src', 'cc'):
            continue
        if m.get(k) in (None, '') and v not in (None, ''):
            m[k] = v
    m['src'] = sorted(set(a['src']) | set(b['src']))
    m['cc'] = sorted(set(a['cc']) | set(b['cc']))
    return m
