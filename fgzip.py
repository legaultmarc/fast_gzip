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
from multiprocessing import Process, Queue


class GzipFileReader(object):

    def __init__(self, fn, chunk_size=128 * 1024):
        """Initialize a GzipFileReader object.

        :param fn: the name of the gzip file
        :type fn: str

        :param chunk_size: the size of the chunk to read from the gzipped file
                           (in bytes).
        :type chunk_size: int

        """
        self.fn = fn
        self._q = Queue(3)
        self._reader_started = False
        self.chunk_size = chunk_size

        # Start process and create the iterator.
        self._reader_proc = Process(target=self._reader_proc)
        self._reader_proc.start()
        self._reader_started = True

        self._iterator = self._parser()

    def readline(self):
        """Reads one line from the gzipped file."""
        for line in self._iterator:
            return line

    def _reader_proc(self):
        """The reader process that reads a chunk from the gzipped file."""
        try:
            with gzip.open(self.fn) as f:
                chunk = f.read(self.chunk_size)
                while chunk:
                    self._q.put(chunk)
                    chunk = f.read(self.chunk_size)

            self._q.put(None)
            self._q.close()
            return

        except KeyboardInterrupt:
            self._q.close()
            return

    def _parser(self):
        """The parser that reads the chunks from a Queue object."""
        fragment = ""
        chunk = self._q.get()

        # new line character is different between python 2.x and 3.x (bytes vs
        # string)
        new_line = "\n"
        if isinstance(chunk[0], int):
            new_line = 10

        while chunk is not None:
            # Split in lines.
            li = chunk.splitlines()

            # If there was a previous fragment, we prepend the first line.
            if fragment != "":
                li[0] = fragment + li[0]
                fragment = ""

            # Maybe the chunk didn't end with a newline.
            # We keep this (new) fragment.
            if not chunk[-1] == new_line:
                fragment = li[-1]
                li = li[:-1]

            for elem in li:
                # Generate line by line
                yield elem

            chunk = self._q.get()

        if fragment:
            yield fragment 

    def next(self):
        """For the generator interface."""
        for i in self._iterator:
            break

    def __next__(self):
        """For the generator interface."""
        return self.next()

    def __iter__(self):
        """For the generator interface."""
        return self._iterator

    def __enter__(self):
        """For the context manager interface."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """For the context manager interface."""
        # Kill the reader process.
        if self._reader_proc.is_alive():
            self._reader_proc.terminate()


def open(fn, chunk_size=None):
    """Opens a new gzipped file using GzipFileReader.

    :param fn: the name of the gzip file
    :type fn: str

    :param chunk_size: the size of the chunk to read from the gzipped file
                        (in bytes).
    :type chunk_size: int

    :returns: a gzipped file parser.
    :rtype: :py:class:`GzipFileReader`

    """
    if chunk_size is not None:
        return GzipFileReader(fn, chunk_size)
    else:
        return GzipFileReader(fn)

