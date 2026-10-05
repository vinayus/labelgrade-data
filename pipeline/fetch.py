"""Download the newest source files.

  python -m pipeline.fetch --dir cache
"""
import argparse
import os
import re
import time
import urllib.request

UA = 'LabelGrade-data/1.0 (+https://github.com/vinayus/labelgrade-data)'
OFF_URL = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'
USDA_PAGE = 'https://fdc.nal.usda.gov/download-datasets'


def get(url, dest=None, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                if dest is None:
                    return r.read().decode('utf-8', 'replace')
                with open(dest + '.part', 'wb') as f:
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
                os.replace(dest + '.part', dest)
                return dest
        except Exception as e:  # flaky mirrors happen; back off and retry
            print(f'  {url}: {e} (try {i + 1}/{tries})', flush=True)
            time.sleep(10 * (i + 1))
    raise SystemExit(f'giving up on {url}')


def latest_usda_url():
    page = get(USDA_PAGE)
    dates = sorted(set(re.findall(r'FoodData_Central_branded_food_csv_(\d{4}-\d{2}-\d{2})\.zip', page)))
    if not dates:
        raise SystemExit('no USDA branded release found on the download page')
    return f'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_branded_food_csv_{dates[-1]}.zip', dates[-1]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='cache')
    d = ap.parse_args().dir
    os.makedirs(d, exist_ok=True)
    url, date = latest_usda_url()
    print(f'USDA branded release {date}', flush=True)
    get(url, os.path.join(d, 'usda.zip'))
    print('Open Food Facts export', flush=True)
    get(OFF_URL, os.path.join(d, 'off.csv.gz'))
    with open(os.path.join(d, 'versions.txt'), 'w') as f:
        f.write(f'usda_branded={date}\noff_export={time.strftime("%Y-%m-%d")}\n')
