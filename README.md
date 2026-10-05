# labelgrade-data

Food label data for [LabelGrade](https://github.com/vinayus/labelgrade), the browser extension that
grades packaged food from its label.

Twice a year a GitHub Action downloads the latest
[Open Food Facts](https://world.openfoodfacts.org) export and the
[USDA FoodData Central](https://fdc.nal.usda.gov) branded-foods release, keeps products with a usable
label (energy, sugars, saturated fat, salt per 100 g, values that can all be true), merges duplicates by
barcode (USDA's manufacturer numbers win, gaps filled from Open Food Facts), and publishes one gzip'd
NDJSON pack per country as a [release](../../releases/latest).

Download a pack: `https://github.com/vinayus/labelgrade-data/releases/latest/download/<country>.ndjson.gz`
(country slugs like `united-kingdom`, `india`, `germany`; products sold in fewer than 50 per country go
in `world`). `index.json` lists every pack with its size and checksum.

## Record format

One JSON object per line:

| key | meaning |
|---|---|
| `b` | barcode, EAN-13 / EAN-8 (UPCs padded to 13 digits) |
| `n`, `br`, `q` | product name, brand, quantity as printed |
| `e` | energy, kJ per 100 g/ml |
| `f`, `sf`, `c`, `s`, `sa`, `fi`, `p` | fat, saturated fat, carbohydrate, sugars, salt, fibre, protein (g per 100 g/ml) |
| `i` | ingredients text (dropped if it looked like junk) |
| `src` | `off` and/or `usda` |
| `cc` | countries where it's sold |

## Build it yourself

```
python -m unittest discover -s tests -t .
python -m pipeline.fetch --dir cache        # ~1.8 GB download
python -m pipeline.build --off cache/off.csv.gz --usda cache/usda.zip --out out
```

Standard library only.

## Licences

- **Data** (the packs): Open Database License (ODbL) 1.0, see [DATA-LICENSE.md](DATA-LICENSE.md).
  Contains information from Open Food Facts, made available under the ODbL, and USDA FoodData Central
  branded foods (public domain).
- **Code** (`pipeline/`, `tests/`): MIT, see [LICENSE](LICENSE).

Spotted a wrong product? Fix it at the source on [Open Food Facts](https://world.openfoodfacts.org); it'll
flow into the next refresh.
