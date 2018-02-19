# char-generator
Dataset generator for OCR - generates character set with modified fonts

---
#### To generate and populate `fonts` directory with fonts
```bash
cd scraper
./make-exec.sh && ./font-scrape
```

`fonts` directory will be generated in callers working directory, ie. `pwd`

#### To create char image directory tree and generate the images
```bash
python3 run.py --prefix="$PREFIX" --charset="$PATH_TO_CHARSET_FILE" \
--fontsdir="$PATH_TO_FONT_DIR"
```
