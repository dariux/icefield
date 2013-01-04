icefield
==========

Amazon Glacier client for large files

Icefield is a Python command-line program intended for *simple* backup and administration of large files using Amazon Glacier. It performs *concurrent* uploads and downloads, and provides automatic inventory bookkeeping through SimpleDB (the archive and vault information is automatically stored in SimpleDB). It can be used from multiple machines, since it does not store archive inventory locally.

Icefield started as a stripped-down version of the Glacier backup tool "bakthat" by Thomas Sileo (https://github.com/tsileo/bakthat).
Don't use icefield for anything important before doing some testing on your own (check out bakthat or glacier-cli instead).


## Installation

Icefield depends on the latest version of boto and aaargh:
    pip install aaargh
    pip install https://github.com/boto/boto/tarball/develop
    pip install https://github.com/dariux/icefield/tarball/master


## Running

To get started, you need to be able to access Amazon services using boto. That means either specifying your credentials using environmental variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` or using `~/.boto` configuration file.
You should also create a Glacier vault in advance using Amazon's Glacier Management console on the web.









