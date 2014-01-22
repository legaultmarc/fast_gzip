#!/usr/bin/python

import gzip
import fgzip
import time

for i in xrange(6):
    if i < -1:#3:
        # Use gzip.
        t1 = time.time()
        j = 0
        with gzip.open('temp.fa.gz') as f:
            for line in f:
                j += 1
        
        t2 = time.time()
        print "Using stdlib gzip, {} lines in {:.4f}s".format(j, t2 - t1)

    else:
        # Use fgzip.
        t1 = time.time()
        j = 0
        with fgzip.open('temp.fa.gz') as f:
            for line in f:
                print line
                quit()
                j += 1
        
        t2 = time.time()
        print "Using fast gzip, {} lines in {:.4f}s".format(j, t2 - t1)

