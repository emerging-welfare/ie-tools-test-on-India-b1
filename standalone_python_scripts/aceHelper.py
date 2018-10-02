import os
import xml.etree.ElementTree
import re
import sys

def getEvents(inpath, myevents, anchors, evsentences, docnames):
    # Read ace
    if os.path.isdir(inpath):
        for filename in os.listdir(inpath):
            if not filename.endswith('apf.xml'):
                continue
            fpath = inpath + filename
            e = xml.etree.ElementTree.parse(fpath).getroot()
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

myevents = []
anchors = []
evsentences = []
docnames = []
getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/bc/adj/', myevents, anchors, evsentences, docnames)
getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/bn/adj/', myevents, anchors, evsentences, docnames)
getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/nw/adj/', myevents, anchors, evsentences, docnames)
getEvents('/home/berfu/ace_2005_td_v7_LDC2006T06/ace_2005_td_v7/data/English/wl/adj/', myevents, anchors, evsentences, docnames)

print('here')