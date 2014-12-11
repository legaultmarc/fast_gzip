#!/usr/bin/env python

# This file is part of fgzip
#
# This work is licensed under the Creative Commons Attribution-NonCommercial
# 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.


__author__ = "Marc-Andre Legault"
__copyright__ = ("Copyright 2014 Marc-Andre Legault and Louis-Philippe Lemieux "
                 "Perreault. All rights reserved.")
__license__ = "Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)"
__credits__ = ["Marc-Andre Legault", "Louis-Philippe Lemieux Perreault"]
__version__ = "0.1"
__maintainer__ = "Marc-Andre Legault"
__email__ = "legaultmarc@gmail.com"
__status__ = "Development"


import gzip

from functools import wraps
from itertools import chain
from multiprocessing import Process, Queue

class GzipFileReader(object):
    """
    An iterable, file-like object that supports
    fast line-based reads of a GZIPed file.
    This does not support the full BufferedIOBase API.
    """

    def __init__(self, filename, chunk_size=128 * 1024):
        self._filename = filename
        self._chunk_queue = Queue(3)
        self._chunk_size = chunk_size

        self._iterator = chain.from_iterable(self._parser())

        # Start process and create the iterator.
        # Do this last to prevent exceptions in
        # the constructor from leaving hanging resources.
        #
        # This ignores the queue, but that's not
        # really worth worrying about if it's empty.
        self._reader_proc = Process(target=self._reader_proc)
        self._reader_proc.start()

    def _reader_proc(self):
        try:
            with gzip.open(self._filename) as f:
                while True:
                    chunk = f.read(self._chunk_size)

                    if not chunk:
                        return

                    self._chunk_queue.put(chunk)

        finally:
            self._chunk_queue.put(None)
            self._chunk_queue.close()

    def _parser(self):
        line_start = None

        while True:
            chunk = self._chunk_queue.get()

            if chunk is None:
                break

            # Split in lines.
            li = chunk.splitlines(keepends=True)

            # If there was a previous line_start, we prepend the first line.
            if line_start is not None:
                li[0] = line_start + li[0]
                line_start = None

            # Maybe the chunk didn't end with a newline.
            # We keep this (new) line_start.
            if not chunk.endswith(b"\n"):
                line_start = li.pop()

            yield li

        if line_start:
            yield [line_start]

    def __next__(self):
        return next(self._iterator)

    readline = __next__

    # Return self._iterator instead of self for faster iteration;
    # is should be very rare for "iter(x) is x" to be required.
    def __iter__(self):
        return self._iterator

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Stop the reader process.
        if self._reader_proc.is_alive():
            self._reader_proc.terminate()

# Alias GzipFileReader
open = wraps(GzipFileReader)(lambda *args: GzipFileReader(*args))
open.__name__ = "open"
