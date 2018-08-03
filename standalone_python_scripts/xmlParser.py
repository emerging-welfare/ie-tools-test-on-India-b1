import xml.etree.ElementTree
import sys

def escape_invalid_char(word):
    word = word.replace('&', "&amp;")
    word = word.replace('<', "&lt;")
    word = word.replace('>', "&gt;")
    word = word.replace('\'', "&apos;")
    word = word.replace('\"', "&quot;")
    return word

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

# args = ['xmlParser.py', '../foliadocs/foliasentences.txt.xml', '../foliadocs/petrarchreadable.xml', '../foliadocs/foliasentenceids.txt' ]
infilepath = args[1]
outfilepath = args[2]
foliadocnamespath = args[3]

xmlparse_stf(infilepath,outfilepath,foliadocnamespath)

print('Operation ended.')

