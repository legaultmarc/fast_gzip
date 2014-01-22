import io
import subprocess
import os.path

class GzipFile():
    def __init__(self, fn, mode='r'):
        self.fn = fn
        self.mode = mode.strip('b')
        if len(self.mode) != 1:
            raise Exception('Invalid mode ({})'.format(mode))

        # Create the file if it does not exist.
        if not os.path.isfile(fn):
            with open(fn, 'w') as f:
                pass

        # We need to create both the input buffer, which will be
        # built on top of a zcat process, and the output buffer, which will
        # build on a gzip process.
        self.read_process = subprocess.Popen(
            # FIXME Change to zcat after dev.
            ['gzcat', self.fn], 
            stdout=subprocess.PIPE
        )

        if self.mode == 'w':
            self.write_process = subprocess.Popen(
                'gzip -c > {}'.format(self.fn),
                shell=True,
                stdin=subprocess.PIPE
            )

    def write(self, s):
        self.write_process.stdin.write(s)

    def readline(self):
        if self.read_process.poll() == 0:
            return None
        else:
            return self.read_process.communicate()[0]

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, 'write_process'):
            self.write_process.communicate()
         
    def next(self):
        # Return a line.
        s = self.readline()
        if s is None:
            raise StopIteration()
        else:
            return s

def open(fn, mode='r'):
    return GzipFile(fn, mode)
