# -*- coding: utf-8 -*-

"""
file: clean.py

Description: remove unwanted fields from a CoNLL-formatted input.

author: Yoann Dupont

MIT License

Copyright (c) 2018 Yoann Dupont

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging, codecs

# measuring time laps
import time
from datetime import timedelta

from .sem_module import SEMModule as RootModule

from sem.misc   import ranges_to_set
from sem.logger import default_handler, file_handler

clean_info_logger = logging.getLogger("sem.clean_info")
clean_info_logger.addHandler(default_handler)

class SEMModule(RootModule):
    def __init__(self, to_keep, log_level="WARNING", log_file=None, **kwargs):
        super(SEMModule, self).__init__(log_level=log_level, log_file=log_file, **kwargs)
        
        if type(to_keep) in (str, unicode):
            self._allowed = to_keep.split(u",") # comma-separated named fields
        else:
            self._allowed = to_keep
        
        if len(self._allowed) == 0:
            raise ValueError("No more data after cleaning !")

    def process_document(self, document, **kwargs):
        """
        Cleans the sem.storage.corpus of a document, removing unwanted fields.
        
        Parameters
        ----------
        document : sem.storage.Document
            the document containing the corpus to clean.
        ranges : str or list of int or list of str
            if str: fields to remove will be induced
            if list of int: each element in the list is the index of a field
            to remove in corpus.fields
            if list of string: the list of fields to remove
        """
        
        start = time.time()
        
        if self._log_file is not None:
            clean_info_logger.addHandler(file_handler(self._log_file))
        clean_info_logger.setLevel(self._log_level)
        
        clean_info_logger.info(u'cleaning document')
        
        allowed = set(self._allowed)
        fields  = set(document.corpus.fields)
        to_remove = [field for field in document.corpus.fields if field not in allowed]
        document.corpus.fields = [field for field in document.corpus.fields if field not in to_remove]
        
        if len(allowed - fields) > 0:
            clean_info_logger.warn(u"the following fields are not present in document, this might cause an error sometime later: %s" %(u", ".join(allowed - fields)))
        
        for i in range(len(document.corpus.sentences)):
            for j in range(len(document.corpus.sentences[i])):
                for field in to_remove:
                    del document.corpus.sentences[i][j][field]
        
        laps = time.time() - start
        clean_info_logger.info(u'done in %s' %timedelta(seconds=laps))

def main(args):
    """
    Cleans a CoNLL-formatted file, removing fields at given indices.
    
    Parameters
    ----------
    args.infile : str
        the name of the file to clean.
    args.outfile : str
        the name of the output file, where some columns have been removed.
    args.ranges : str
        the fields to remove. Fields is a coma-separated list of indices
        or ranges of indices using a python format (ie: "lo:hi").
    """
    
    if args.log_file is not None:
        clean_info_logger.addHandler(file_handler(args.log_file))
    clean_info_logger.setLevel(args.log_level)
    
    ienc = args.ienc or args.enc
    oenc = args.oenc or args.enc
    
    allowed = ranges_to_set(args.ranges, len(codecs.open(args.infile, "rU", ienc).readline().strip().split()), include_zero=True)
    max_abs = 0
    for element in allowed:
        element = abs(element) + (1 if element > 0 else 0)
        max_abs = max(max_abs, element)
    nelts = len(codecs.open(args.infile, "rU", ienc).readline().strip().split())
    
    if nelts < max_abs:
        clean_info_logger.error(u'asked to keep up to %i field(s), yet only %i are present in the "%s"' %(max_abs, nelts, args.infile))
        raise runtimeError(u'asked to keep up to %i field(s), yet only %i are present in the "%s"' %(max_abs, nelts, args.infile))
    
    clean_info_logger.info(u'cleaning "%s"' %(args.infile))
    clean_info_logger.info(u'keeping columns: %s' %(u", ".join([str(s) for s in sorted(allowed)])))
    clean_info_logger.info(u'writing "%s"' %(args.outfile))
        
    with codecs.open(args.outfile, "w", oenc) as O:
        for line in codecs.open(args.infile, "rU", ienc):
            line = line.strip().split()
            if line != []:
                tokens = [line[i] for i in xrange(len(line)) if i in allowed]
                O.write(u"\t".join(tokens))
            O.write(u"\n")
    
    clean_info_logger.info(u'done')


import os.path
import sem

_subparsers = sem.argument_subparsers

parser = _subparsers.add_parser(os.path.splitext(os.path.basename(__file__))[0], description="Remove unwanted columns from CoNLL-formatted file.")

parser.add_argument("infile",
                    help="The input file")
parser.add_argument("outfile",
                    help="The output file ")
parser.add_argument("ranges",
                    help="The ranges of indexes to keep in the file.")
parser.add_argument("--input-encoding", dest="ienc",
                    help="Encoding of the input (default: UTF-8)")
parser.add_argument("--output-encoding", dest="oenc",
                    help="Encoding of the input (default: UTF-8)")
parser.add_argument("--encoding", dest="enc", default="UTF-8",
                    help="Encoding of both the input and the output (default: UTF-8)")
parser.add_argument("-l", "--log", dest="log_level", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"), default="WARNING",
                    help="Increase log level (default: critical)")
parser.add_argument("--log-file", dest="log_file",
                    help="The name of the log file")
