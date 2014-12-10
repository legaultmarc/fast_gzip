This is a very small module to read ``gzip`` files. It was inspired by a 
discussion on [reddit](http://www.reddit.com/r/Python/comments/2olhrf/fast_gzip_in_python/).

It starts a subprocess that fills a queue with uncompressed data and the main
class parses lines from this queue.

Usage:

```python

import fgzip

with fgzip.open("my_large_file.gz") as f:
    for line in f:
        print line

```

