"""
file: chunking_fscore.py

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

import sys, codecs

from sem.IO.columnIO import Reader

from sem.features import MultiwordDictionaryFeature, NUL

import sem.importers

def compile_chunks(sentence, column=-1):
    entity_chunks = set()
    label         = u""
    start         = -1
    for index, token in enumerate(sentence):
        ne = token[column]
        
        if ne == "O":
            if label:
                entity_chunks.add(tuple([label, start, index]))
                label = u""
                start = -1
        elif ne[0] == "B":
            if label:
                entity_chunks.add(tuple([label, start, index]))
            start = index
            label = ne[2:]
        elif ne[0] == "I":
            None
        else:
            raise ValueError(ne)
    if label:
        entity_chunks.add(tuple([label, start, index]))
        label = u""
        start = -1
    
    return entity_chunks


def float2spreadsheet(f):
    """
    For spreadsheets, dots should be replaced by commas.
    """
    return (u"%.2f" %f).replace(u".",u",")


def main(args):
    infile = args.infile
    reference_column = args.reference_column
    tagging_column = args.tagging_column
    ienc = args.ienc or args.enc
    oenc = args.oenc or args.enc
    verbose = args.verbose
    input_format = args.input_format
    
    counts = {}
    prf = {}
    if input_format == "conll":
        for p in Reader(infile, ienc):
            reference = compile_chunks(p, column=reference_column)
            tagging = compile_chunks(p, column=tagging_column)
            ok = reference & tagging
            silence = reference - ok
            noise = tagging - ok
            for e in ok:
                label = e[0]
                if label not in counts:
                    counts[label] = {"ok":0.0, "gold":0.0, "guess":0.0}
                counts[label]["ok"] += 1.0
                counts[label]["gold"] += 1.0
                counts[label]["guess"] += 1.0
            for e in silence:
                label = e[0]
                if label not in counts:
                    counts[label] = {"ok":0.0, "gold":0.0, "guess":0.0}
                counts[label]["gold"] += 1.0
            for e in noise:
                label = e[0]
                if label not in counts:
                    counts[label] = {"ok":0.0, "gold":0.0, "guess":0.0}
                counts[label]["guess"] += 1.0
        counts[""] = {"ok":0.0, "gold":0.0, "guess":0.0}
        for label in counts:
            if label == "": continue
            counts[""]["ok"] += counts[label]["ok"]
            counts[""]["gold"] += counts[label]["gold"]
            counts[""]["guess"] += counts[label]["guess"]
    elif input_format == "brat":
        tagging_document = sem.importers.brat_file(infile)
        reference_document = sem.importers.brat_file(args.reference_file)
        tagging_annotations = tagging_document.annotation("NER").get_reference_annotations()
        reference_annotations = reference_document.annotation("NER").get_reference_annotations()
        """tagging = set([tuple([ann.value, ann.lb, ann.ub]) for ann in tagging_annotations])
        reference = set([tuple([ann.value, ann.lb, ann.ub]) for ann in reference_annotations])
        ok = reference & tagging
        silence = reference - ok
        noise = tagging - ok
        for e in ok:
            label = e[0]
            if label not in counts:
                counts[label] = {"ok":0.0, "gold":0.0, "guess":0.0}
            counts[label]["ok"] += 1.0
            counts[label]["gold"] += 1.0
            counts[label]["guess"] += 1.0
        for e in silence:
            label = e[0]
            if label not in counts:
                counts[label] = {"ok":0.0, "gold":0.0, "guess":0.0}
            counts[label]["gold"] += 1.0
        for e in noise:
            label = e[0]
            if label not in counts:
                counts[label] = {"ok":0.0, "gold":0.0, "guess":0.0}
            counts[label]["guess"] += 1.0
        counts[""] = {"ok":0.0, "gold":0.0, "guess":0.0}"""
        
        boundary_errors = set() # the set of already aligned entities in gold (may be aligned twice)
        
        L = tagging_annotations
        R = reference_annotations
        
        d = {"correct":[], "type":[], "boundary":[], "type+boundary":[], "silence":[], "noise":[]}
        # first pass, removing correct
        i = 0
        print "corrects", len(L), len(R)
        while i < len(L):
            LR = L[i]
            j = 0
            while j < len(R):
                RR = R[j]
                if LR == RR:
                    del L[i]
                    del R[j]
                    i -= 1
                    d["correct"].append([LR, RR])
                    break
                j += 1
            i += 1
        
        # second pass, typing errors
        i  = 0
        print "type", len(L), len(R)
        while i < len(L):
            LR = L[i]
            j = 0
            while j < len(R):
                RR = R[j]
                if LR.value != RR.value and LR.lb == RR.lb and LR.ub == RR.ub:
                    del L[i]
                    del R[j]
                    d["type"].append([LR, RR])
                    break
                j += 1
            i += 1
        
        # third pass, boundary errors
        i  = 0
        print "boundary", len(L), len(R)
        while i < len(L):
            LR = L[i]
            j = 0
            while j < len(R):
                RR = R[j]
                if LR.value == RR.value and ((LR.lb != RR.lb and LR.ub == RR.ub) or (LR.lb == RR.lb and LR.ub != RR.ub)):
                    del L[i]
                    del R[j]
                    i -= 1
                    d["boundary"].append([LR, RR])
                    break
                j += 1
            i += 1
        
        # fourth pass, both type and boundary errors
        i  = 0
        print "type+boundary", len(L), len(R)
        while i < len(L):
            LR = L[i]
            j = 0
            while j < len(R):
                RR = R[j]
                if LR.value != RR.value and (LR.lb != RR.lb and LR.lb == RR.ub) or (LR.lb == RR.lb and LR.lb != RR.ub):
                    del L[i]
                    del R[j]
                    i -= 1
                    d["type+boundary"].append([LR, RR])
                    break
                j += 1
            i += 1
        
        print len(L), len(R)
        d["silence"] = L[:]
        d["noise"] = R[:]
        
        for key, value in d.items():
            print key, len(value)
    else:
        raise RuntimeError("format not handled")
    
    for label in counts:
        lbl_c = counts[label]
        ok = lbl_c["ok"]
        gold = lbl_c["gold"]
        guess = lbl_c["guess"]
        
        prf[label] = {"p":0.0, "r":0.0, "f":0.0}
        if guess != 0.0:
            prf[label]["p"] = 100.0 * ok / guess
        if gold != 0.0:
            prf[label]["r"] = 100.0 * ok / gold
        if prf[label]["p"] + prf[label]["r"] != 0.0:
            prf[label]["f"] = 2.0 * ((prf[label]["p"] * prf[label]["r"]) / (prf[label]["p"] + prf[label]["r"]))
    
    print "entity\tprecision\trecall\tf-measure"
    entities = set(prf.keys())
    entities.discard("")
    entities = sorted(entities)
    for entity in entities:
        e_prf = prf[entity]
        print "%s\t%s\t%s\t%s" %(entity, float2spreadsheet(e_prf["p"]), float2spreadsheet(e_prf["r"]), float2spreadsheet(e_prf["f"]))
    ma_p = sum([prf[entity]["p"] for entity in entities]) / (len(entities))
    ma_r = sum([prf[entity]["r"] for entity in entities]) / (len(entities))
    ma_f = 2.0 * (ma_p * ma_r) / (ma_p + ma_r)
    print
    print "%s\t%s\t%s\t%s" %("micro-average", float2spreadsheet(prf[""]["p"]), float2spreadsheet(prf[""]["r"]), float2spreadsheet(prf[""]["f"]))
    print "%s\t%s\t%s\t%s" %("macro-average", float2spreadsheet(ma_p), float2spreadsheet(ma_r), float2spreadsheet(ma_f))


import os.path
import sem

_subparsers = sem.argument_subparsers

parser = _subparsers.add_parser(os.path.splitext(os.path.basename(__file__))[0], description="Get F1-score for tagging using the IOB scheme.")

parser.add_argument("infile",
                    help="The input file (CoNLL format)")
parser.add_argument("-r", "--reference-column", dest="reference_column", type=int, default=-2,
                    help="Column for reference output (default: %(default)s)")
parser.add_argument("-t", "--tagging-column", dest="tagging_column", type=int, default=-1,
                    help="Column for CRF output (default: %(default)s)")
parser.add_argument("-f", "--format", dest="input_format", default="conll",
                    help="The input format (default: %(default)s)")
parser.add_argument("-c", "--reference-file", dest="reference_file",
                    help="The comparing file")
parser.add_argument("--input-encoding", dest="ienc",
                    help="Encoding of the input (default: utf-8)")
parser.add_argument("--output-encoding", dest="oenc",
                    help="Encoding of the input (default: utf-8)")
parser.add_argument("-e", "--encoding", dest="enc", default="utf-8",
                    help="Encoding of both the input and the output (default: utf-8)")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                    help="Writes feedback during process (default: no output)")
