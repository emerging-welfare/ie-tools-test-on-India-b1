from pynlpl.formats import folia
import os
import re
import sys

def convertFoliaClass2ConllTag(e):
    per = 'I-PER'
    loc = 'I-LOC'
    org = 'I-ORG'
    cls = e.cls
    if re.match('^.*Target.*$', e.set):
        if cls == 'name':
            return per
    elif re.match('^.*Organizer.*$', e.set):
        if cls == 'name':
            return org
    if cls == 'loc' or cls == 'place' or cls == 'place_pub':
        return loc
    if cls == 'pname':
        return per
    if cls == 'fname':
        return org
    return 'O'


def convertFoliaClass2stfTag(e):
    per = 'PERSON'
    loc = 'LOCATION'
    org = 'ORGANIZATION'
    cls = e.cls
    if re.match('^.*Target.*$', e.set):
        if cls == 'name':
            return per
    elif re.match('^.*Organizer.*$', e.set):
        if cls == 'name':
            return org
    if cls == 'loc' or cls == 'place' or cls == 'place_pub':
        return loc
    if cls == 'pname':
        return per
    if cls == 'fname':
        return org
    return 'O'


def readFoliaIntoSentences(path):
    sentences_as_tokens = []
    ids = []
    id2idx = {}
    idx2id = {}
    all_tokens = []
    actual_stf_tags = []
    if os.path.isdir(path):
        idx = -1
        for filename in os.listdir(path):
            doc = folia.Document(file=path + '/' + filename)
            for h, sentence in enumerate(doc.sentences()):
                sentence_tokenized = sentence.select(folia.Word)
                words_folia = list(sentence_tokenized)
                sentence_tokens = []
                for word in words_folia:
                    w_id = word.id
                    w_text = word.text()
                    if w_id in ids:
                        continue
                    idx = idx + 1
                    if idx == 16307 and w_text == '<P>':
                        idx = idx - 1
                        continue
                    ids.append(w_id)
                    id2idx[w_id] = idx
                    idx2id[idx] = w_id
                    actual_stf_tags.append('O')
                    sentence_tokens.append(w_text)
                    all_tokens.append(w_text)

                sentences_as_tokens.append(sentence_tokens)
                for layer in sentence.select(folia.EntitiesLayer):
                    for entity in layer.select(folia.Entity):
                        for word in entity.wrefs():
                            word_id = word.id
                            _idx = id2idx[word_id]
                            stf_tag = convertFoliaClass2stfTag(entity)
                            actual_stf_tags[_idx] = stf_tag

    else:
        print("TODO: Handling of a single Folia file instead of a folder of Folia files.")
    return [sentences_as_tokens, ids, id2idx, idx2id, all_tokens, actual_stf_tags]


def doc2conll(fp, sentences, ids, id2token, id2tag, idx, conllfile):

    doc = folia.Document(file=fp)
    for h, sentence in enumerate(doc.sentences()):
        sentence_tokenized = sentence.select(folia.Word)
        words_folia = list(sentence_tokenized)
        sentence_tokens = []  # sentence as token ids
        for word in words_folia:
            w_id = word.id
            w_text = word.text()
            if w_id in ids:
                continue
            idx = idx + 1
            if idx == 16307 and w_text == '<P>':
                idx = idx - 1
                continue
            sentence_tokens.append(w_id)
            id2token[w_id] = w_text
            id2tag[w_id] = 'O'

            ids.append(w_id)

            sentences.append(sentence_tokens)
        for layer in sentence.select(folia.EntitiesLayer):
            for entity in layer.select(folia.Entity):
                for word in entity.wrefs():
                    word_id = word.id
                    conll_tag = convertFoliaClass2ConllTag(entity)
                    id2tag[word_id] = conll_tag

        for _id in sentence_tokens:
            line = id2token[_id] + " " + id2tag[_id] + "\n"
            conllfile.write(line)

        conllfile.write("\n")


def folia2conll(flpath, opath):
    sentences = []  # A sentence is a list of token ids.
    ids = []
    id2token = {}
    id2tag = {}
    conll_file = open(opath, 'w')

    idx = -1
    if os.path.isdir(flpath):
        for filename in os.listdir(flpath):
            fpath = flpath + '/' + filename
            doc2conll(fpath, sentences, ids, id2token, id2tag, idx, conll_file)
    else:
        doc2conll(flpath, sentences, ids, id2token, id2tag, idx, conll_file)

    print('Folia docs are converted to conll format')
    conll_file.close()


args = sys.argv

folder = './foliadocs/alladjudicated'
single_file = './foliadocs/alladjudicated/' \
              'https__timesofindia.indiatimes.com_business_india-business_BSNL-Employees-Union-protests-against-disinvestment_articleshow_972751.folia.xml'

# args = ['foliaHelper.py', 'folia2conll', folder, './folia_as_conll_test.txt']
if len(args) <= 1:
    print("Please specify the operation then the input file. For help, type 'python foliaHelper.py -h\n")
    sys.exit()
elif args[1] == '-h':
    print('example usage: \n python foliaHelper.py folia2conll foliafile outfile \n '
          'foliafile: file or folder containing folia formatted content \n'
          'outfile: output file path')
else:
    oper = args[1]
    foliafile = args[2]
    outfile = args[3]

    if oper == 'folia2conll':
        folia2conll(foliafile, outfile)
    else:
        print('TODO: change code of other helper functions to allow calling from command prompt.\n')
        sys.exit()

