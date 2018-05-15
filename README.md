# mdshare
Get access to our MD data files.

[![CircleCI](https://circleci.com/gh/markovmodel/mdshare/tree/master.svg?style=svg)](https://circleci.com/gh/markovmodel/mdshare/tree/master)

This is a downloader for molecular dynamics (MD) data from a public FTP server at FU Berlin. See https://markovmodel.github.io/mdshare/ for a full list of available datasets and terms of use.

## Example
This code will download a file (if it does not already exist locally) with a featurized set of three alanine dipeptide MD trajectories and store its content of three ``numpy.ndarray`` objects (each of ``shape=[250000, 2], dtype=numpy.float32``) in the list ``trajs``:
```python
import mdshare
import numpy as np

local_filename = mdshare.fetch('alanine-dipeptide-3x250ns-backbone-dihedrals.npz')
with np.load(local_filename) as fh:
    trajs = [fh[key] for key in fh.keys()]
```

By default, the ``mdshare.fetch()`` function will look in and download to the current directory (function parameter ``working_directory='.'``). If you instead set this parameter to ``None``,
```python
local_filename = mdshare.fetch(
    'alanine-dipeptide-3x250ns-backbone-dihedrals.npz',
    working_directory=None)
```
the file will be downloaded to a temporary directory with a randomly chosen name. In both cases, the function will return the path to the local file.

Should the requested file already be present in the ``working_directory``, the download is skipped.

Use ``mdshare.catalogue()`` to view the files and filesizes of the available trajectories:

```python
mdshare.catalogue()
```
Produces the output:
```
alanine-dipeptide-0-250ns-nowater.dcd                        86 MB
alanine-dipeptide-1-250ns-nowater.dcd                        86 MB
alanine-dipeptide-2-250ns-nowater.dcd                        86 MB
alanine-dipeptide-3x250ns-backbone-dihedrals.npz             6 MB
...
```

Use ``mdshare.search(filename_pattern)`` to select for a given group of files:

```python
pentapeptide_xtcs = mdshare.search('penta*xtc')
print(pentapeptide_xtcs)
```
Produces the output:
```
['pentapeptide-00-500ns-impl-solv.xtc',
 'pentapeptide-01-500ns-impl-solv.xtc',
 'pentapeptide-02-500ns-impl-solv.xtc',
...
 'pentapeptide-22-500ns-impl-solv.xtc',
 'pentapeptide-23-500ns-impl-solv.xtc',
 'pentapeptide-24-500ns-impl-solv.xtc']
```