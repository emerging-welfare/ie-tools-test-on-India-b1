import re
import sys
import os
import xml.etree.ElementTree

def evalrpi(rpirespath, eventsrefpath, outfolderpath):
    eventinfo = open(eventsrefpath, 'r')
    events = eventinfo.readlines()
    eventslist = []
    for line in events:
        if len(line.strip()) > 0:
            if len(eventslist) == 0:
                eventslist.append([])
            eventslist[-1].append(line.strip())
        else:
            eventslist.append([])

    docnames = [e[0] for e in eventslist]
    eventwords = [e[1:] for e in eventslist]
    eventwordsall = [y for x in eventwords for y in x]

   # read rpi output
    tp_anchors = []
    pred_anchors = []
    fp_anchors = []
    numtrueanchors = 0
    numpredanchors = 0
    tp_event_sents = []
    tp_event_docnames = []
    tp_subtypes = []
    tp_tense = []
    fp_event_sents = []
    fp_event_docnames = []
    fp_subtypes = []
    fp_tense = []
    if os.path.isdir(rpirespath):
        for filename in os.listdir(rpirespath):
            fpath = rpirespath + filename
            e = xml.etree.ElementTree.parse(fpath).getroot()
            doc = e.find('document')
            res = doc.getchildren()
            events = [r for r in res if r.tag == 'event']
            if len(events) > 0:
                dpath = doc.attrib['DOCID']
                match = re.match(r"^.*input/(.*)\.sgm.*$", dpath)
                dname = match.group(1)

                for ev in events:
                    subtype = ev.attrib['SUBTYPE']
                    tense = ev.attrib['TENSE']
                    em = ev.find('event_mention')
                    ex = em.find('extent')
                    tx = ex.find('charseq').text
                    a = em.find('anchor')
                    numpredanchors += 1
                    cs = a.find('charseq')
                    w = cs.text

                    if dname not in docnames:
                        fp_event_sents.append(tx)
                        fp_event_docnames.append(dname)
                        fp_anchors.append(w)
                        fp_subtypes.append(subtype)
                        fp_tense.append(tense)
                    else:
                        idx = docnames.index(dname)
                        ewords = eventwords[idx]
                        if w in ewords:
                            numtrueanchors += 1
                            tp_event_sents.append(tx)
                            tp_event_docnames.append(dname)
                            tp_anchors.append(w)
                            tp_subtypes.append(subtype)
                            tp_tense.append(tense)
                        else:
                            fp_event_sents.append(tx)
                            fp_event_docnames.append(dname)
                            fp_anchors.append(w)
                            fp_subtypes.append(subtype)
                            fp_tense.append(tense)


    precision = numtrueanchors/numpredanchors
    recall = numtrueanchors/len(eventwordsall)
    f1 = 2*precision*recall/(precision + recall)
    # recall: to be able to find recall we need to map anchors to etypes by id. One way to do this is to use charseq start-ends if
    # it is fairly easier than propogating word ids to rpi output.
    tp_anchors_set = set(tp_anchors)
    fn_anchors_set = set(eventwordsall) - tp_anchors_set
    fp_anchors_set = set(fp_anchors)

    """TP EXAMINATION"""
    # Demonstration orani
    # Hangilerine demonstration demis
    # Hangilerine baska bir sey demis/ne demis
    tp_demon_idx = [i for i in range(len(tp_anchors)) if tp_subtypes[i] == 'Demonstrate']
    tp_attack_idx = [i for i in range(len(tp_anchors)) if tp_subtypes[i] == 'Attack']
    tp_other_idx = [i for i in range(len(tp_anchors)) if i not in tp_demon_idx and i not in tp_attack_idx]
    """FP EXAMINATION"""
    # Demonstration dediklerinin orani
    # Hangilerine demonstration demis
    fp_demon_idx = [i for i in range(len(fp_anchors)) if fp_subtypes[i] == 'Demonstrate']
    fp_attack_idx = [i for i in range(len(fp_anchors)) if fp_subtypes[i] == 'Attack']
    fp_other_idx = [i for i in range(len(fp_anchors)) if i not in fp_demon_idx and i not in fp_attack_idx]

    fp_demon_sents = [fp_event_sents[i] for i in fp_demon_idx]
    fp_demon_anchors = [fp_anchors[i] for i in fp_demon_idx]
    fp_demon_tense = [fp_tense[i] for i in fp_demon_idx]
    fp_demon_docnames = [fp_event_docnames[i] for i in fp_demon_idx]
    import pandas as pd
    d = {'anchor': pd.Series(fp_demon_anchors),
         'tense': pd.Series(fp_demon_tense),
         'sentence': pd.Series(fp_demon_sents),
         'doc': pd.Series(fp_demon_docnames)}
    fp_demon = pd.DataFrame(d, columns=['anchor', 'tense', 'sentence', 'doc'])
    fp_demon.to_csv(outfolderpath + 'rpi_fp_demonstrate.csv')

    # Strike
    '''tp_strike_idx = [i for i in range(len(tp_anchors)) if tp_anchors[i] == 'strike']
    len(tp_strike_idx)
    Out[3]: 102
    fp_strike_idx = [i for i in range(len(fp_anchors)) if fp_anchors[i] == 'strike']
    len(fp_strike_idx)
    Out[5]: 10
    tp_strike_subtype = [tp_subtypes[i] for i in tp_strike_idx]
    fp_strike_subtype = [fp_subtypes[i] for i in fp_strike_idx]
    tp_num_strike_demon = len([s for s in tp_strike_subtype if s == 'Attack'])
    tp_num_strike_demon
    Out[9]: 102
    fp_num_strike_demon = len([s for s in fp_strike_subtype if s == 'Attack'])
    fp_num_strike_demon
    Out[11]: 10'''

    """TP FP INTERSECTION"""
    tp_event_sents_set = set(tp_event_sents)
    fp_event_sents_set = set(fp_event_sents)
    tp_fp_inter = tp_event_sents_set.intersection(fp_event_sents_set)
    sen2docname = {}
    sen2tp_anchors = {}
    sen2fp_anchors = {}
    sen2tp_tenses = {}
    sen2tp_subtypes = {}
    sen2fp_tenses = {}
    sen2fp_subtypes = {}
    sen2tp_indices = {}
    sen2fp_indices = {}

    for sen in tp_fp_inter:
        tp_indices = [i for i, x in enumerate(tp_event_sents) if x == sen]
        sen2tp_indices[sen] = tp_indices
        sen2docname[sen] = tp_event_docnames[tp_indices[0]]
        fp_indices = [i for i, x in enumerate(fp_event_sents) if x == sen]
        sen2tp_anchors[sen] = [tp_anchors[i] for i in tp_indices]
        sen2fp_anchors[sen] = [fp_anchors[i] for i in fp_indices]
        sen2tp_tenses[sen] = [tp_tense[i] for i in tp_indices]
        sen2tp_subtypes[sen] = [tp_subtypes[i] for i in tp_indices]
        sen2fp_tenses[sen] = [fp_tense[i] for i in fp_indices]
        sen2fp_subtypes[sen] = [fp_subtypes[i] for i in fp_indices]

    of = open(outfolderpath + 'rpieval.txt', 'w+')
    of.write('Precision (number of truly predicted anchors/number of predicted anchors) - document-wise string check - : ' + str(precision) + '\n\n')
    of.write('Recall (number of truly predicted anchors/number of actually annotated anchors) - document-wise string check - : ' + str(recall) + '\n')
    of.write('F1 measure: ' + str(f1) + '\n\n')

    #of.write('True positive anchors:\n\n')
    #for t in list(tp_anchors_set):
    #    of.write(t + '\n')
    #of.write('\n\n\n\nFalse positive anchors:\n\n')
    #for m in list(fp_anchors_set):
     #   of.write(m + '\n')

    of.write('\n\n\n\nTrue positive anchors - rpi sents:\n\n')
    for i,tp in enumerate(tp_anchors):
        of.write(tp_subtypes[i] + '\t' +  tp_tense[i] + '\t' + tp + '\t' +  tp_event_sents[i] + '\t' + tp_event_docnames[i] + '\n\n')
    of.write('\n\n\n\nFalse positive anchors - rpi sents:\n\n')
    for i, fp in enumerate(fp_anchors):
        of.write(fp_subtypes[i] + '\t' +  fp_tense[i] + '\t' + fp + '\t' + fp_event_sents[i] + '\t' + fp_event_docnames[i] + '\n\n')

    of.write('\n\n\n\nSentences predicted to have both tp and fp events/anchors: \n\n')
    for s in tp_fp_inter:
        of.write('\n\n\n' + s + '\n')
        docnm = sen2docname[sen]
        of.write(docnm + '\n')
        tpanchors = sen2tp_anchors[s]
        tptenses = sen2tp_tenses[s]
        tpsubtps = sen2tp_subtypes[s]
        for i,a in enumerate(tpanchors):
            of.write('tp' + '\t' + a + '\t' + tptenses[i] + '\t' + tpsubtps[i] + '\n')
        fpanchors = sen2fp_anchors[s]
        fptenses = sen2fp_tenses[s]
        fpsubtps = sen2fp_subtypes[s]
        for i, a in enumerate(fpanchors):
            of.write('fp' + '\t' + a + '\t' + fptenses[i] + '\t' + fpsubtps[i] + '\n')


    of.write('\n\n\n\nFalse negative anchors:\n\n')
    for m in list(fn_anchors_set):
        of.write(m + '\n')
    of.close()


def evalpetrarch(petrarchrespath,eventsrefpath,outfilepath):
    petrarchres = open(petrarchrespath, 'r')
    eventinfo = open(eventsrefpath, 'r')
    events = eventinfo.readlines()
    eventslist = []
    for line in events:
        if len(line.strip()) > 0:
            if len(eventslist) == 0:
                eventslist.append([])
            eventslist[-1].append(line.strip())
        else:
            eventslist.append([])

    sentenceids = [e[0] for e in eventslist]
    eventidword = [e[1:] for e in eventslist]
    wordspersentence = []
    eventidspersentence = []

    for i,s in enumerate(sentenceids):
        wordspersentence.append([])
        eventidspersentence.append([])
        eidwords = eventidword[i]
        for eidword in eidwords:
            eid = re.split(r'\t', eidword)[0]
            word = re.split(r'\t', eidword)[1]
            wordspersentence[-1].append(word)
            eventidspersentence[-1].append(eid)


    eidword = [re.split(r'\t', idword[0]) for idword in eventidword]
    eventids = [idword[0] for idword in eidword]
    eventwords = [idword[1] for idword in eidword]

    predevents = petrarchres.readlines()
    predevents1 = [line for line in predevents if line.strip()] # nonempty lines
    predevents2 = [predevents1[x:x + 2] for x in range(0, len(predevents1), 2)]

    predfirstlines = [p[0] for p in predevents2]
    # predfirstlines = [x.split() for x in predfirstlines]
    predwordspersentence = [p.split('TOI',1)[1].strip().split() for p in predfirstlines] # take string after word TOI (arbitrary StorySource text I added to every sentence in the xml because it is required.)
    predsentenceids = [p[1].strip() for p in predevents2]

    true_sentence = 0
    true_eventids = []
    true_word = 0

    true_word_indices = []
    allwidx = -1
    for i, predsentenceid in enumerate(predsentenceids):
        if predsentenceid not in sentenceids:
            continue
        true_sentence += 1
        idx = sentenceids.index(predsentenceid)
        ewords = predwordspersentence[i] # predicted event related words in the sentence (words after 'TOI')
        for eword in ewords:
            allwidx += 1
            if eword in wordspersentence[idx]:  # check if word exists in any of events of that sentence
                true_word += 1
                true_word_indices.append(allwidx)
                widx = wordspersentence[idx].index(eword)
                eid = eventidspersentence[idx][widx]  # id of the event that word belongs.
                true_eventids.append(eid)  # add event id the detected events list. That list might contain duplicates

    numtrueeventsfound = len(set(true_eventids))
    actualnumevents = len(set(eventids))

    recall = round(numtrueeventsfound/actualnumevents,2)
    precision = round(numtrueeventsfound/len(predsentenceids),2)
    f1 = round(2*recall*precision/(recall+precision),2)

    true_words_found = set([eventwords[i] for i in true_word_indices])
    true_words_missed = set([eventwords[i] for i in range(0,len(eventwords)) if i not in true_word_indices])

    outfile = open(outfilepath, 'w')
    outfile.write('Recall: ' + str(recall) + '\n')
    outfile.write('Precision: ' + str(precision) + '\n')
    outfile.write('F1: ' + str(f1) + '\n')
    outfile.write('Event related words truly detected (' + str(len(true_words_found)) + '): ' + str(true_words_found) + '\n')
    outfile.write('Event related words missed (' + str(len(true_words_missed)) + '): ' + str(true_words_missed) + '\n')
    outfile.close()

args = sys.argv
# args = ['utilEval.py', 'petrarch', '../foliadocs/evts.petrarchreadable_out_lower.txt','../foliadocs/foliasentenceideventidword.txt','../foliadocs/petrarcheval.txt']
args = ['utilEval.py', 'rpi', '../foliadocs/rpi/output/','../foliadocs/folia_docnameetypewords.txt','../foliadocs/rpi/']
resultpath = args[2]  # "../foliadocs/evts.petrarchreadable_out_lower.txt"
referencepath = args[3]  # "../foliadocs/foliasentenceideventidword.txt"
outfilepath = args[4]  # "../foliadocs/petrarcheval.txt"

if args[1] == 'petrarch':
    evalpetrarch(resultpath, referencepath, outfilepath)
elif args[1] == 'rpi':
    evalrpi(resultpath, referencepath, outfilepath)
    # NOTE: rpi output files should have ids created by the function 'text2rpiinput' in xmlParser.py for a regex expression to work in the evalrpi function.
    # So please follow the rpi pipeline on README or be aware of the regex situation.


