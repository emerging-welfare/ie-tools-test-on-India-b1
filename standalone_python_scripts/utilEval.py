import re
import sys

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
# args = ['utilEval.py','../foliadocs/evts.petrarchreadable_out_lower.txt','../foliadocs/foliasentenceideventidword.txt','../foliadocs/petrarcheval.txt']

petrarchresultpath = args[1]  # "../foliadocs/evts.petrarchreadable_out_lower.txt"
eventreferencepath = args[2]  # "../foliadocs/foliasentenceideventidword.txt"
outfilepath = args[3] # "../foliadocs/petrarcheval.txt"

evalpetrarch(petrarchresultpath,eventreferencepath, outfilepath)

