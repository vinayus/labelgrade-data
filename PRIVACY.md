# LabelGrade privacy policy

_Last updated: 5 October 2026_

LabelGrade is a browser extension that shows ingredient-based grades on product pages of supported shopping sites.

## What it reads
LabelGrade reads the product page you are viewing on a supported shop: the product title, ingredient list, nutrition table, barcode if shown, and product photos. Reading and grading happen on your computer.

Product photos are downloaded from the shop's own image servers and read with an OCR engine that runs inside the extension, on your computer. Photos are not uploaded anywhere.

## LabelGrade's own label database
To look products up without sending anything about them, LabelGrade downloads a label database for the
country of the shop you're on (for example India or the UK) from LabelGrade's public data repository on
GitHub (github.com/vinayus/labelgrade-data), once, and checks for an update at most once a week. Lookups in
it happen on your computer. GitHub sees the download request like any website does.

## What it sends, and only if you allow it
If a page doesn't show the full label, LabelGrade asks once whether it may look the product up in public food databases. If you say yes, it sends **only the product name and/or barcode** to:
- USDA FoodData Central (api.nal.usda.gov), run by the U.S. Department of Agriculture
- Open Food Facts (world.openfoodfacts.org), a non-profit open database

These services receive your IP address as part of any web request, as all websites do. Their own privacy policies apply. If you say no, LabelGrade sends nothing.

## What it stores
- One setting: whether you allowed database lookups (stored in your browser).
- Lookup and OCR results, cached in your browser for the current session only.
- The downloaded label database for the countries you've shopped in, until you remove the extension.

## What it doesn't do
- No account, no analytics, no tracking, no ads, no affiliate links.
- It doesn't collect your browsing history, and it doesn't run on sites other than the supported shops.
- It doesn't sell or share data with anyone.

## Changes
Changes to this policy are noted here with a new date.

## Contact
Email vteam2005@yahoo.com, or open an issue at https://github.com/vinayus/labelgrade-data/issues (questions, corrections and privacy requests).
