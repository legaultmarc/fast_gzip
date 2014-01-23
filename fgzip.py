#!/usr/bin/env python

import subprocess
import os.path

STDLIB_OPEN = open

class GzipFile():
    BUFSIZE = 4096 * 1000

    def __init__(self, fn, mode='r'):
        self.fn = fn
        self.mode = mode.strip('b')
        if len(self.mode) != 1:
            raise Exception('Invalid mode ({})'.format(mode))

        # Create the file if it does not exist.
        if not os.path.isfile(fn):
            with STDLIB_OPEN(fn, 'w') as f:
                pass

        # We need to create either the input buffer, which will be
        # built on top of a zcat process, or the output buffer, which will
        # build on a gzip process.
        if self.mode == 'r':
            self.read_process = subprocess.Popen(
                # FIXME Change to zcat after dev.
                ['gzcat', self.fn], 
                stdout=subprocess.PIPE,
                bufsize = GzipFile.BUFSIZE
            )

        if self.mode == 'w':
            self.write_process = subprocess.Popen(
                'gzip -c > {}'.format(self.fn),
                shell=True,
                stdin=subprocess.PIPE,
                bufsize = GzipFile.BUFSIZE
            )

    def write(self, s):
        if self.mode != 'w':
            raise Exception("Can't write to file with mode 'r'.")
        self.write_process.stdin.write(s)

    def readline(self):
        if self.mode != 'r':
            raise Exception("Can't read from a file with mode 'w'.")

        line = self.read_process.stdout.readline()
        if line == '':
            return None
        else:
            return line.rstrip('\r\n')

    def __iter__(self):
        return iter(self.read_process.stdout.readline, '')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, 'write_process'):
            self.write_process.communicate()
         
    def next(self):
        pass

def open(fn, mode='r'):
    return GzipFile(fn, mode)

def compare_md5(fn1, fn2):
    import re, sh

    sum1 = re.split(r'\s+', sh.md5sum(fn1).stdout)[0]
    sum2 = re.split(r'\s+', sh.md5sum(fn2).stdout)[0]
    return sum1 == sum2

def compare_compressed(fn1, fn2):
    import gzip

    with gzip.open(fn1) as f1:
        with gzip.open(fn2) as f2:
            l1 = f1.readline()
            l2 = f2.readline()

            while l1 == l2 and l1 != '':
                l1 = f1.readline()
                l2 = f2.readline()

            return l1 == l2

def test():

    import gzip
    import sh
    import re

    import benchmarks

    print "Running Tests..."

    temp_fgz = '.test_fgz.fgziptest'
    temp_std = '.test_std.fgziptest'

    # Check reading
    test_file = 'test_files/compressed.fa.gz'

    with STDLIB_OPEN(temp_std, 'wb') as out:
        with gzip.open(test_file) as f:
            for line in f:
                out.write(line)

    with STDLIB_OPEN(temp_fgz, 'wb') as out:
        with GzipFile(test_file) as f:
            for line in f:
                out.write(line)

    s = 'Read compressed file test '
    if compare_md5(temp_fgz, temp_std):
        s += '[PASS]'
    else:
        s += '[FAIL]'

    for i in (temp_std, temp_fgz):
        sh.rm(i)
    print s

    # Check writing
    test_file = 'test_files/text.fa'

    with STDLIB_OPEN(test_file) as f:
        with gzip.open(temp_std, 'wb') as out:
            for line in f:
                out.write(line)

    with STDLIB_OPEN(test_file) as f:
        with GzipFile(temp_fgz, 'wb') as out:
            for line in f:
                out.write(line)   

    s = 'Compress file test (write) '
    if compare_compressed(temp_fgz, temp_std):
        s += '[PASS]'
    else:
        s += '[FAIL]'

    for i in (temp_std, temp_fgz):
        sh.rm(i)
    print s

    # Run benchmarks
    print
    print 'Running speed benchmarks...'
    benchmarks.benchmark()

if __name__ == "__main__":
    test()
