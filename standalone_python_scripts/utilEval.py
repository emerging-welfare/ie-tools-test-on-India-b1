import re
import sys
import os
import xml.etree.ElementTree

def evalrpi(rpirespath, eventsrefpath, outfilepath):
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
    tp_event_nuggets = []
    tp_event_docnames = []
    fp_event_nuggets = []
    fp_event_docnames = []
    if os.path.isdir(rpirespath):
        for filename in os.listdir(rpirespath):
            fpath = rpirespath + filename
            e = xml.etree.ElementTree.parse(fpath).getroot()
            doc = e.find('document')
            res = doc.getchildren()
            events = [r for r in res if r.tag == 'event']
            if len(events) > 0:
                dpath = doc.attrib['DOCID']
                match = re.match(r"^.*test/(.*)\.sgm.*$", dpath)
                dname = match.group(1)
                idx = docnames.index(dname)

                for ev in events:
                    em = ev.find('event_mention')
                    a = em.find('anchor')
                    numpredanchors += 1
                    cs = a.find('charseq')
                    w = cs.text
                    ewords = eventwords[idx]
                    ex = em.find('extent')
                    tx = ex.find('charseq').text
                    if w in ewords:
                        numtrueanchors += 1
                        tp_event_nuggets.append(tx)
                        tp_event_docnames.append(dname)
                        tp_anchors.append(w)
                    else:
                        fp_event_nuggets.append(tx)
                        fp_event_docnames.append(dname)
                        fp_anchors.append(w)

    precision = numtrueanchors/numpredanchors
    # recall: to be able to find recall we need to map anchors to etypes by id. One way to do this is to use charseq start-ends if
    # it is fairly easier than propogating word ids to rpi output.
    tp_anchors_set = set(tp_anchors)
    fn_anchors_set = set(eventwordsall) - tp_anchors_set
    fp_anchors_set = set(fp_anchors)
    of = open(outfilepath, 'w+')
    of.write('Precision (number of truly predicted anchors/number of predicted anchors) - document-wise checked - : ' + str(precision) + '\n\n')
    #of.write('True positive anchors:\n\n')
    #for t in list(tp_anchors_set):
    #    of.write(t + '\n')
    #of.write('\n\n\n\nFalse positive anchors:\n\n')
    #for m in list(fp_anchors_set):
     #   of.write(m + '\n')
    of.write('\n\n\n\nTrue positive anchors - rpi nuggets:\n\n')
    for i,tp in enumerate(tp_anchors):
        of.write(tp + '\t' + tp_event_nuggets[i] + '\t' + tp_event_docnames[i] + '\n\n')
    of.write('\n\n\n\nFalse positive anchors - rpi nuggets:\n\n')
    for i, fp in enumerate(fp_anchors):
        of.write(fp + '\t' + fp_event_nuggets[i] + '\t' + fp_event_docnames[i] + '\n\n')
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
args = ['utilEval.py', 'petrarch', '../foliadocs/evts.petrarchreadable_out_lower.txt','../foliadocs/foliasentenceideventidword.txt','../foliadocs/petrarcheval.txt']
# args = ['utilEval.py', 'rpi', '../foliadocs/rpi/output/','../foliadocs/folia_docnameetypewords.txt','../foliadocs/rpieval.txt']
resultpath = args[2]  # "../foliadocs/evts.petrarchreadable_out_lower.txt"
referencepath = args[3]  # "../foliadocs/foliasentenceideventidword.txt"
outfilepath = args[4]  # "../foliadocs/petrarcheval.txt"

if args[1] == 'petrarch':
    evalpetrarch(resultpath, referencepath, outfilepath)
elif args[1] == 'rpi':
    evalrpi(resultpath, referencepath, outfilepath)
    # NOTE: rpi output files should have ids created by the function 'text2rpiinput' in xmlParser.py for a regex expression to work in the evalrpi function.
    # So please follow the rpi pipeline on README or be aware of the regex situation.


