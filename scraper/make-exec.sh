#!/bin/bash

[ -z `find . -name 'font-scrape.py'` ] && echo "MISSING font-scrape.py" 1>&2 && exit 1

EXEC_FILE='font-scrape'

{ printf '#!/bin/env python3\n' && cat "font-scrape.py"; } > $EXEC_FILE

chmod +x $EXEC_FILE
