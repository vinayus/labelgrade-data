import csv, gzip, io, json, os, tempfile, unittest, zipfile
from pipeline.build import build

OFF_COLS = ['code', 'product_name', 'brands', 'quantity', 'countries_en', 'energy-kj_100g', 'energy-kcal_100g', 'fat_100g',
            'saturated-fat_100g', 'carbohydrates_100g', 'sugars_100g', 'salt_100g', 'sodium_100g', 'fiber_100g', 'proteins_100g', 'ingredients_text']

def off_file(path, rows):
    with gzip.open(path, 'wt', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, OFF_COLS, delimiter='\t')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in OFF_COLS})

def usda_file(path):
    def table(cols, rows):
        s = io.StringIO(); w = csv.writer(s); w.writerow(cols); w.writerows(rows); return s.getvalue()
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('FoodData_Central_branded_food_csv_2026-04-30/food.csv',
                   table(['fdc_id', 'data_type', 'description'], [['1', 'branded_food', 'FROOT LOOPS CEREAL']]))
        z.writestr('FoodData_Central_branded_food_csv_2026-04-30/food_nutrient.csv',
                   table(['id', 'fdc_id', 'nutrient_id', 'amount'], [['a', '1', '1008', '380'], ['b', '1', '1004', '3.5'], ['c', '1', '1258', '1.7'],
                         ['d', '1', '1005', '86'], ['e', '1', '2000', '34.5'], ['f', '1', '1093', '520'], ['g', '1', '1003', '6.9']]))
        z.writestr('FoodData_Central_branded_food_csv_2026-04-30/branded_food.csv',
                   table(['fdc_id', 'brand_owner', 'brand_name', 'gtin_upc', 'ingredients', 'package_weight', 'market_country', 'discontinued_date'],
                         [['1', 'Kellogg', "KELLOGG'S", '038000198885', '', '14.7 oz', 'United States', '']]))

class Build(unittest.TestCase):
    def test_end_to_end(self):
        d = tempfile.mkdtemp()
        off_file(f'{d}/off.csv.gz', [
            dict(code='38000198885', product_name='Froot Loops', brands="Kellogg's", countries_en='United States,Canada',
                 **{'energy-kj_100g': '1600', 'fat_100g': '3.5', 'saturated-fat_100g': '1.7', 'carbohydrates_100g': '86', 'sugars_100g': '33',
                    'salt_100g': '1.3', 'ingredients_text': 'corn flour, sugar, wheat flour, oat fiber, salt'}),
            dict(code='5000159484695', product_name='Bad row', brands='X', countries_en='United Kingdom',
                 **{'energy-kj_100g': '1500', 'fat_100g': '2', 'saturated-fat_100g': '9', 'sugars_100g': '5', 'salt_100g': '0.1'}),
        ] + [dict(code=f'50{i:011d}', product_name=f'UK thing {i}', brands='Brand', countries_en='United Kingdom',
                  **{'energy-kj_100g': '1000', 'sugars_100g': '5', 'saturated-fat_100g': '1', 'fat_100g': '3', 'salt_100g': '0.5'}) for i in range(1, 61)])
        usda_file(f'{d}/usda.zip')
        build(f'{d}/off.csv.gz', f'{d}/usda.zip', f'{d}/out')

        idx = json.load(open(f'{d}/out/index.json'))
        self.assertIn('united-kingdom', idx['packs'])
        self.assertIn('world', idx['packs'])           # US/Canada have <50 products here
        lines = [json.loads(l) for l in gzip.open(f'{d}/out/world.ndjson.gz', 'rt')]
        loops = next(r for r in lines if r['b'] == '0038000198885')
        self.assertEqual(loops['s'], 34.5)             # USDA numbers win
        self.assertTrue(loops['i'].startswith('corn flour'))  # ingredients filled from OFF
        self.assertEqual(sorted(loops['src']), ['off', 'usda'])
        uk = [json.loads(l) for l in gzip.open(f'{d}/out/united-kingdom.ndjson.gz', 'rt')]
        self.assertEqual(len(uk), 60)                  # the impossible 'Bad row' is gone
        self.assertEqual(idx['products'], 61)

if __name__ == '__main__':
    unittest.main()
