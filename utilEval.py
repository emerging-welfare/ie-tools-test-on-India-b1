import sys
import os


def runconlleval(infile, outfile):
    python_path = sys.executable
    os.system(python_path + ' conlleval.py -r < ' + infile + ' > ' + outfile)
    print('Please see the scores wrt conlleval script in the file: ' + outfile + '\n')