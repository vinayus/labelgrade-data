"""Readers for the two sources. Both stream, so memory stays sane on a GitHub runner."""
import csv
import gzip
import io
import sys
import zipfile

from .clean import record, num, country_slug

csv.field_size_limit(sys.maxsize)


def read_off(path):
    """Open Food Facts CSV export (tab separated, gzip). ODbL."""
    with gzip.open(path, 'rt', encoding='utf-8', errors='replace', newline='') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            kj = num(row.get('energy-kj_100g'))
            if kj is None:
                kcal = num(row.get('energy-kcal_100g'))
                kj = kcal * 4.184 if kcal is not None else None
            salt = num(row.get('salt_100g'))
            if salt is None and num(row.get('sodium_100g')) is not None:
                salt = num(row.get('sodium_100g')) * 2.5
            yield record(
                barcode=row.get('code'), name=row.get('product_name'), brand=row.get('brands'),
                quantity=row.get('quantity'), energy_kj=kj, fat=num(row.get('fat_100g')),
                sat_fat=num(row.get('saturated-fat_100g')), carbs=num(row.get('carbohydrates_100g')),
                sugars=num(row.get('sugars_100g')), salt=salt, fiber=num(row.get('fiber_100g')),
                protein=num(row.get('proteins_100g')), ingredients=row.get('ingredients_text'),
                source='off', countries=[country_slug(c) for c in (row.get('countries_en') or '').split(',')],
            )


# FoodData Central nutrient ids (branded foods report per 100 g)
NUTRIENTS = {1062: 'kj', 1008: 'kcal', 1004: 'fat', 1258: 'sat', 1005: 'carbs', 2000: 'sugars', 1063: 'sugars_nlea',
             1079: 'fiber', 1003: 'protein', 1093: 'sodium'}


def _csv(z, name):
    member = next(n for n in z.namelist() if n.endswith('/' + name) or n == name)
    return csv.DictReader(io.TextIOWrapper(z.open(member), encoding='utf-8', errors='replace', newline=''))


def read_usda(path):
    """USDA FoodData Central branded foods CSV zip. Public domain."""
    with zipfile.ZipFile(path) as z:
        names = {r['fdc_id']: r['description'] for r in _csv(z, 'food.csv') if r.get('data_type') == 'branded_food'}
        values = {}
        for r in _csv(z, 'food_nutrient.csv'):
            key = NUTRIENTS.get(int(r['nutrient_id'] or 0))
            if key and r['fdc_id'] in names:
                values.setdefault(r['fdc_id'], {})[key] = num(r['amount'])
        for r in _csv(z, 'branded_food.csv'):
            fid = r['fdc_id']
            if fid not in names or r.get('discontinued_date'):
                continue
            v = values.get(fid, {})
            kj = v.get('kj') if v.get('kj') is not None else (v['kcal'] * 4.184 if v.get('kcal') is not None else None)
            sugars = v.get('sugars') if v.get('sugars') is not None else v.get('sugars_nlea')
            salt = v['sodium'] * 2.5 / 1000 if v.get('sodium') is not None else None
            pkg = r.get('package_weight') or ''
            yield record(
                barcode=r.get('gtin_upc'), name=names[fid], brand=r.get('brand_name') or r.get('brand_owner'),
                quantity=pkg, energy_kj=kj, fat=v.get('fat'), sat_fat=v.get('sat'), carbs=v.get('carbs'),
                sugars=sugars, salt=salt, fiber=v.get('fiber'), protein=v.get('protein'),
                ingredients=r.get('ingredients'), source='usda',
                countries=[country_slug(r.get('market_country') or 'United States')],
            )
