import unittest
from pipeline.clean import normalize_barcode, num, looks_like_ingredients, sane, merge, country_slug, record

class Barcodes(unittest.TestCase):
    def test_upc12_padded_to_13(self):
        self.assertEqual(normalize_barcode('038000198885'), '0038000198885')
    def test_ean13_and_ean8_kept(self):
        self.assertEqual(normalize_barcode('5000159484695'), '5000159484695')
        self.assertEqual(normalize_barcode('96385074'), '96385074')
    def test_gtin14_with_leading_zero_trimmed(self):
        self.assertEqual(normalize_barcode('00038000198885'), '0038000198885')
    def test_lost_leading_zeros_restored(self):
        # OFF often stores UPCs as numbers, so the leading zero goes missing
        self.assertEqual(normalize_barcode('38000198885'), '0038000198885')
        self.assertEqual(normalize_barcode('6385074'), '06385074')
    def test_junk_rejected(self):
        for b in ('', 'abc', '12', None, '0000000000000'):
            self.assertIsNone(normalize_barcode(b), b)

class Numbers(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(num('1,5'), 1.5)
        self.assertEqual(num('12'), 12.0)
        for v in ('', None, 'nan', '-3', 'abc'):
            self.assertIsNone(num(v), v)

class Ingredients(unittest.TestCase):
    def test_real_list(self):
        self.assertTrue(looks_like_ingredients('sugar, glucose syrup, starch, invert sugar syrup, citric acid'))
    def test_junk(self):
        self.assertFalse(looks_like_ingredients('480x UK 0800 604604 se UK Lad, PO Box 207, York, Y'))
        self.assertFalse(looks_like_ingredients('PROSIVES'))

def rec(**kw):
    base = dict(barcode='0038000198885', name='Froot Loops', brand="Kellogg's", quantity='14.7 oz', energy_kj=1600.0,
                fat=3.5, sat_fat=1.7, carbs=86.0, sugars=34.0, salt=1.3, fiber=10.0, protein=6.9,
                ingredients='corn flour, sugar, wheat flour, oat fiber, salt', source='off', countries=['united-states'])
    base.update(kw)
    return record(**base)

class Sanity(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(sane(rec()))
    def test_missing_core(self):
        self.assertFalse(sane(rec(sugars=None)))
        self.assertFalse(sane(rec(energy_kj=None)))
    def test_impossible_values(self):
        self.assertFalse(sane(rec(sat_fat=7.7, fat=3.8)))      # saturated above total fat
        self.assertFalse(sane(rec(sugars=90.0, carbs=80.0)))   # sugars above carbs
        self.assertFalse(sane(rec(energy_kj=5000.0)))          # more than pure fat (~3700)
        self.assertFalse(sane(rec(salt=120.0)))                # over 100 g per 100 g
    def test_junk_ingredients_dropped_not_rejected(self):
        r = rec(ingredients='PROSIVES')
        self.assertTrue(sane(r))
        self.assertEqual(r['i'], '')

class Merge(unittest.TestCase):
    def test_usda_nutrition_wins_ingredients_filled(self):
        off = rec(source='off', sugars=33.0, ingredients='corn flour, sugar, wheat flour, oat fiber, salt', countries=['canada'])
        usda = rec(source='usda', sugars=34.5, ingredients='', countries=['united-states'])
        m = merge(off, usda)
        self.assertEqual(m['s'], 34.5)
        self.assertTrue(m['i'].startswith('corn flour'))
        self.assertEqual(sorted(m['cc']), ['canada', 'united-states'])
        self.assertEqual(sorted(m['src']), ['off', 'usda'])

class Countries(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(country_slug('United Kingdom'), 'united-kingdom')
        self.assertEqual(country_slug('en:india'), 'india')
        self.assertEqual(country_slug(' Côte d\'Ivoire '), 'cote-d-ivoire')

if __name__ == '__main__':
    unittest.main()
