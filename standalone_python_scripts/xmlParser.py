import xml.etree.ElementTree
import sys

def escape_invalid_char(word):
    word = word.replace('&', "&amp;")
    word = word.replace('<', "&lt;")
    word = word.replace('>', "&gt;")
    word = word.replace('\'', "&apos;")
    word = word.replace('\"', "&quot;")
    return word

# Creates rpi input xml.
def text2rpiinput(infile, outfolder):
    f = open(infile, "r")
    allinput = f.readlines()
    sentences = []
    for line in allinput:
        if len(line.strip()) > 0:
            if len(sentences) == 0:
                sentences.append([])
            sentences[-1].append(line.strip())
        else:
            sentences.append([])

    docnames = [e[0] for e in sentences]
    sentencelist = [e[1:] for e in sentences] # doc2sentences

    lstfile = open(outfolder + 'test.lst',  "w+")
    for i,docname in enumerate(docnames):
        lstfile.write(docname + '.sgm' + '\n')
        outxml = open(outfolder + docname + '.sgm', "w+")
        outxml.write("<DOC>\n")
        outxml.write('<DOCID>' + docname + '</DOCID>\n')
        outxml.write('<DOCTYPE SOURCE="newswire"> NEWS STORY </DOCTYPE>\n') # dummy
        outxml.write('<DATETIME> 20030325 </DATETIME>\n') # dummy
        outxml.write('<BODY>\n')
        outxml.write('<HEADLINE> dummy headline </HEADLINE>\n')
        outxml.write("<TEXT>\n")
        sents = sentencelist[i]
        for i, sent in enumerate(sents):
            outxml.write(sent + '\n')
        outxml.write("</TEXT>\n")
        outxml.write('</BODY>\n')  # dummy
        outxml.write("</DOC>\n")
        outxml.close()

    print('Sentences and their parses are written to a file in xml format.\n')
    lstfile.close()

# Creates PETRARCH2 input xml.
def xmlparse_stf(infile, outfile, sentenceidsfile):
    e = xml.etree.ElementTree.parse(infile).getroot()

    d = e.find("document")
    ss = d.find("sentences")
    sents = ss.getchildren()
    sentences = []
    parses = []
    for sent in sents:
        sentences.append("")
        tokens = sent.find("tokens")
        parse = sent.find("parse")
        parse_text = escape_invalid_char(parse.text)
        parses.append(parse_text)
        idx = -1
        for i, token in enumerate(tokens):
            w = token.find("word")
            wt = escape_invalid_char(w.text)
            if i + 1 < len(tokens):
                sentences[-1] = sentences[-1] + wt + ' '
            elif i + 1 == len(tokens):
                sentences[-1] = sentences[-1] + wt
            else:
                print('Should not hit here. Investigate.\n')

    print('Sentences and their parses are retrieved.\n')

    if len(sentences) <= 0:
        sys.exit()
    else:
        sentenceidsf = open(sentenceidsfile, "r")
        sentenceids = sentenceidsf.readlines()
        sentenceids = [x.strip() for x in sentenceids]  # refs

        outxml = open(outfile, "w+")
        outxml.write("<Sentences>\n")

        for i, sent in enumerate(sentences):
            outxml.write("<Sentence date = \"" + str(20180729) + "\" id = \"" + str(i) + "_" + str(
                i) + "\" source = \"TOI\" sentence = \"True\">\n")
            outxml.write("<Text>\n")
            outxml.write(sent + '\n')
            outxml.write("</Text>\n")
            outxml.write("<Parse>\n")
            outxml.write(parses[i] + '\n')
            outxml.write("</Parse>\n")
            outxml.write("<Ref>\n")
            outxml.write(sentenceids[i] + '\n')
            outxml.write("</Ref>\n")
            outxml.write("</Sentence>\n")

        outxml.write("</Sentences>\n")

        print('Sentences and their parses are written to a file in xml format.\n')

args = sys.argv

args = ['xmlParser.py', 'petrarch2', '../foliadocs/foliasentences1.txt.xml', '../foliadocs/petrarchreadable.xml', '../foliadocs/foliasentenceids1.txt' ]
# '../foliadocs/foliasentences.txt.xml': Stanford core nlp's output (we will use pos tags)
# '../foliadocs/petrarchreadable.xml': output file path to be used by petrarch2 as input later.
# '../foliadocs/foliasentenceids.txt': sentence ids of all of the folia docs are listed. This info will also be included
# into the petrarchreadable.xml, for petrarch2 will access it and print out to the output file.

# args = ['xmlParser.py', 'rpi', '../foliadocs/foliadocnamesentenceshavingevents.txt', '../foliadocs/rpi/input1/']

if args[1] == 'petrarch2':
    infilepath = args[2]
    outfilepath = args[3]
    foliadocnamespath = args[4]
    xmlparse_stf(infilepath, outfilepath, foliadocnamespath)
elif args[1] == 'rpi':
    infilepath = args[2]
    outfilepath = args[3]
    text2rpiinput(infilepath,outfilepath)

print('Operation ended.')

