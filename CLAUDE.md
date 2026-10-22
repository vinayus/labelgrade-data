# labelgrade-data: working notes

Data for the LabelGrade extension (code and the full working notes live in
`github.com/vinayus/labelgrade`, see its `CLAUDE.md`).

- `pipeline/` (Python stdlib only): `fetch.py` downloads the Open Food Facts CSV export and the USDA
  FoodData Central branded-foods zip, `clean.py` keeps products with a usable label and normalises
  barcodes (must match `normalizeBarcode()` in the extension's `src/core/packs.js`), `build.py` merges by
  barcode and writes one gzip'd NDJSON pack per country plus `index.json`. Tests in `tests/`.
- `.github/workflows/refresh.yml` runs on 15 Jan and 15 May and publishes the **Latest** release; the
  extension downloads `releases/latest/download/<country>.ndjson.gz`.
- Release `ocr-data-1`: OCR language files (Tesseract best_int from `@tesseract.js-data/*` 4.0.0, MIT)
  that the extension fetches on demand and checks by SHA-256. Never mark it "latest", never delete or
  replace its files; new files go in a new `ocr-data-N` release.
- Licences: data ODbL (`DATA-LICENSE.md`), code MIT. `PRIVACY.md` is the extension's privacy policy
  (linked from the Chrome Web Store), so keep its URL stable.
- Open decision: Korean product data (data.go.kr dataset 15100066 via API key as a secret, or a manual
  CSV twice a year; dataset 15112364 is KOGL Type 4 and can't be used).
