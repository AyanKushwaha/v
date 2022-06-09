import re
import mmap
import os

class Searcher(object):

    def __init__(self, file, regexp, verbose = False):

        if os.path.getsize(file) != 0:
            file = open(file, 'r')
            self.file_data = file.read()
            file.close()
        else:
            self.file_data = ""

        compiled_regexp = re.compile(regexp, re.MULTILINE)

        self.reg_iter = compiled_regexp.finditer(self.file_data)
        self.verbose = verbose
        self.nof_lines = 0
    
    def __iter__(self):
        return self

    def next(self):

        match = self.reg_iter.next()

        if match is None:            
            raise StopIteration

        return match.groupdict()
        
        
