import os
import xml.etree.ElementTree as ET
from pynlpl.formats import folia
import sys


'''
bn: text-turn (a single turn)
bc: text-turn (multiple turns)
wl: text-post (single post)
nw: text
'''

'''
def escape_invalid_char(filepath):
    word = word.replace('&', "&amp;")
    word = word.replace('<', "&lt;")
    word = word.replace('>', "&gt;")
    word = word.replace('\'', "&apos;")
    word = word.replace('\"', "&quot;")
    return word
'''

def readacefile(foldername,filepath):
    prgs = []
    ''' Im here: 
    escape_invalid_char(filepath) escape ampersand etc
    '''
    d = ET.parse(filepath).getroot()
    b = d.find("BODY")
    txs = b.findall("TEXT")
    for tx in txs:
        if foldername == 'bn':
            trs = tx.findall("TURN")
            for tr in trs:
                prg = tr.text
                prg = prg.replace('\n', " ").strip()
                if prg != "": prgs.append(prg)
        elif foldername == 'bc':
            trs = tx.findall("TURN")
            for tr in trs:
                prg = ''.join(tr.itertext())
                exclude1 = tr.find('SPEAKER').text
                prg = prg.replace(exclude1, "")
                prg = prg.replace('\n', " ").strip()
                if prg != "": prgs.append(prg)
        elif foldername == 'wl':
            pss = tx.findall("POST")
            for ps in pss:
                prg = ''.join(ps.itertext())
                exclude1 = ps.find('POSTER').text
                exclude2 = ps.find('POSTDATE').text
                prg = prg.replace(exclude1, "")
                prg = prg.replace(exclude2, "")
                prg = prg.replace('\n', " ").strip()
                if prg != "": prgs.append(prg)
        elif foldername == 'nw':
            prg = tx.text
            prg = prg.replace('\n', " ").strip()
            if prg != "": prgs.append(prg)
    return prgs

def extracttext(inpath,foldername):
    filetexts = [] # list of lists. each list contains text in a single file.
    adjfolderpath = inpath + '/' + foldername + '/adj'
    for filename in os.listdir(adjfolderpath):
        if filename.endswith('sgm'):
            filepath = adjfolderpath + '/' + filename
            print('Filepath: ' + filepath + '\n')
            texts = readacefile(foldername,filepath) # list: texts in a single file. if file does not contain any text, it is empty list.
            filetexts.append(texts)
    return filetexts

# Creates ace sentences file from ace sgm files - raw text files
def ace2sentences(inpath, outpath, acesubfolders):
    outf = open(outpath, 'w+')
    if os.path.isdir(inpath):
        for foldername in os.listdir(inpath):
            if foldername in acesubfolders:
                textslist = extracttext(inpath, foldername) # list of list of files. Each list contain texts of a single file. if file does not contain any text, it is empty list.

        # write all texts in a single file
        for texts in textslist:
            for text in texts:
                outf.write(text + '\n\n')

    print('Ace texts were extracted to a single file.')

def getEvents(inpath, myevents, anchors, evsentences, docnames):
    # Read ace
    if os.path.isdir(inpath):
        for filename in os.listdir(inpath):
            if not filename.endswith('apf.xml'):
                continue
            fpath = inpath + filename
            e = ET.parse(fpath).getroot()
            doc = e.find('document')
            res = doc.getchildren()
            events = [r for r in res if r.tag == 'event']

            if len(events) > 0:
                for i in range(len(events)):
                    ev = events[i]
                    subtype = ev.attrib['SUBTYPE']
                    tense = ev.attrib['TENSE']
                    em = ev.find('event_mention')
                    ldc = em.find('ldc_scope')
                    tx = ldc.find('charseq').text
                    a = em.find('anchor')
                    cs = a.find('charseq')
                    w = cs.text
                    myevents.append(subtype)
                    anchors.append(w)
                    evsentences.append(tx)
                    docnames.append(filename)

    '''
    strike_sentences = [s[1] for s in enumerate(evsentences) if anchors[s[0]] == 'strike']
    strike_sentences_idx = [s[0] for s in enumerate(evsentences) if anchors[s[0]] == 'strike']
    strike_sentences_docnames = [d[1] for d in enumerate(docnames) if d[0] in strike_sentences_idx]
    strike_sentences_subtypes = [d[1] for d in enumerate(myevents) if d[0] in strike_sentences_idx]
    '''

args = sys.argv

infile = '/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English'
outfile = '../foliadocs/acesentences.txt'
acesubfolders = ['bc','bn','nw','wl']
args = ['utilFormat.py', 'ace2sentences', infile, outfile]

if len(args) <= 1:
    print("Please specify the operation then the input and output files."
          " For help, type 'python neuroNERoutfileHelper.py -h\n")
    sys.exit()
elif args[1] == '-h':
    print('example usage: \n python utilFormat.py \n '
          'conll2raw: convert conll tags to raw tags | \n'
          'folia2conll: convert folia to conll format \n'
          'infile: the file having token - actual tag - predicted tag \n'
          'outfile: infile\'s version with raw tags \n')
elif args[1] == 'ace2sentences':
    infile = args[2]
    outfile = args[3]
    ace2sentences(infile, outfile, acesubfolders)
elif args[1] == 'getEvents':
    myevents = []
    anchors = []
    evsentences = []
    docnames = []
    getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/bc/adj/', myevents, anchors,
              evsentences, docnames)
    getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/bn/adj/', myevents, anchors,
              evsentences, docnames)
    getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/nw/adj/', myevents, anchors,
              evsentences, docnames)
    getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/wl/adj/', myevents, anchors,
              evsentences, docnames)
