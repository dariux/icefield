icefield
========

Python Glacier client for large files

This is a stripped-down version of the Glacier backup tool "bakthat" by Thomas Sileo (https://github.com/tsileo/bakthat).
Icefield is intended for *simple* backup and administration of large files using Amazon Glacier. 
It now has automatic inventory bookkeeping through SimpleDB (the archive and vault information is automatically stored in SimpleDB).

Don't use icefield for anything important yet, it has not been extensively tested yet (check out bakthat or glacier-cli instead)