#!/usr/bin/env python

import io
import gzip
import argparse
from multiprocessing import Process, Queue

def _reader(fn, queue, chunk_size=128 * 1000):
    with gzip.open(fn) as f:
        chunk = f.read(chunk_size)
        while chunk:
            queue.put(chunk)
            chunk = f.read(chunk_size)

    queue.put(None)
    queue.close()
    return


def _parser(queue):
    fragment = ""
    chunk = queue.get()
    while chunk is not None:
        # Split in lines.
        li = chunk.splitlines()

        # If there was a previous fragment, we prepend the first line.
        if fragment != "":
            li[0] = fragment + li[0]
            fragment = ""

        # Maybe the chunk didn't end with a newline.
        # We keep this (new) fragment.
        if not chunk.endswith("\n"):
            fragment = li[-1]
            li = li[:-1]

        for elem in li:
            # Generate line by line
            yield elem

        chunk = queue.get()

    if fragment:
        yield fragment


class GzipFileReader(object):

    def __init__(self, fn, chunk_size=128 * 1024):
        self.fn = fn
        self._q = Queue(3)
        self._reader_started = False
        self._fragment = ""
        self.chunk_size = chunk_size

    def readline(self):
        # Check if reader started.
        if not self._reader_started:
            # Start the process
            self._reader_proc = Process(target=self._reader_proc)
            self._reader_proc.start()
            self._reader_started = True

        return self._parser.next()

    def _reader_proc(self):
        print "Started reader process"
        with gzip.open(self.fn) as f:
            chunk = f.read(self.chunk_size)
            while chunk:
                self._q.put(chunk)
                chunk = f.read(self.chunk_size)

        self._q.put(None)
        self._q.close()
        return

    def _parser(self):
        fragment = ""
        chunk = self._q.get()
        while chunk is not None:
            # Split in lines.
            li = chunk.splitlines()

            # If there was a previous fragment, we prepend the first line.
            if fragment != "":
                li[0] = fragment + li[0]
                fragment = ""

            # Maybe the chunk didn't end with a newline.
            # We keep this (new) fragment.
            if not chunk.endswith("\n"):
                fragment = li[-1]
                li = li[:-1]

            for elem in li:
                # Generate line by line
                yield elem

            chunk = self._q.get()

        if fragment:
            yield fragment 


def read_gzip(fn):
    # Start a thread that reads the gzip file and pushes the data in a queue.
    q = Queue()

    reader = Process(target=_reader, args=(fn, q))
    reader.start()

    # Count the lines in the file.
    i = 0
    for line in _parser(q):
        i += 1
    print i

    reader.join()

