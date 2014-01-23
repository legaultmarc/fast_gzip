#!/usr/bin/python

import gzip
import fgzip
import time
import os

def benchmark(n = 6):

    print "READ BENCHMARK"
    for i in xrange(n):
        if i < n / 2:
            # Use gzip.
            t1 = time.time()
            j = 0
            with gzip.open('test_files/compressed.fa.gz') as f:
                for line in f:
                    j += 1
            
            t2 = time.time()
            print "\tUsing stdlib gzip, {} lines in {:.4f}s".format(j, t2 - t1)

        else:
            # Use fgzip.
            t1 = time.time()
            j = 0
            with fgzip.open('test_files/compressed.fa.gz') as f:
                for line in f:
                    j += 1
            
            t2 = time.time()
            print "\tUsing fast gzip, {} lines in {:.4f}s".format(j, t2 - t1)

    print "WRITE BENCHMARK"
    for i in xrange(n):
        if i < n / 2:
            # Use gzip.
            t1 = time.time()
            with open('test_files/text.fa') as f:
                with gzip.open('.fgzip_benchmark.txt.gz', 'wb') as f2:
                    for line in f:
                        f2.write(line)

            t2 = time.time()
            print "\tUsing stdlib gzip, compressed in {:.4f}s".format(t2 - t1)

        else:
            # Use fgzip.
            t1 = time.time()
            with open('test_files/text.fa') as f:
                with fgzip.open('.fgzip_benchmark.txt.gz', 'wb') as f2:
                    for line in f:
                        f2.write(line)           

            t2 = time.time()
            print "\tUsing fast gzip, compressed in {:.4f}s".format(t2 - t1)

    os.remove('.fgzip_benchmark.txt.gz')

if __name__ == "__main__":
     benchmark()
