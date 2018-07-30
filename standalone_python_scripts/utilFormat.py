from pynlpl.formats import folia
import os
import re
import sys


# clear tags from initial parts (I-LOC to LOC, etc)
# I required this operation to evaluate NeuroNER prediction results on folia docs.
# The reason is that the predictor outputs conll formatted tags such as I-LOC, B-LOC.
# However, for folia docs I do  not have information about tag initials.
# Since NeuroNER accepts decent conll formatted test files as output, I had to assign initials to tags.
# And I arbitrarily assigned I, at the beginning of each tag - except for O and MISC.


# Now after prediction, default conlleval evaluates the results regarding the initials as well as the tags.
# This brings an additional error to the results.
# So for better understanding, with this code I omit the initials for both the actual and predicted tags.
# Conlleval has also an option named -r. It assumes the tags are "raw': initial-free.


def conll2raw(outfile, resfile):
    with open(outfile) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        content_list = [x.split() for x in content]

        for line in content_list:
            if len(line) == 0:
                continue
            act = line[-2]
            pred = line[-1]

            a = act.split('-')
            p = pred.split('-')

            if len(a) > 1: act = a[1]
            if len(p) > 1: pred = p[1]
            line[-2] = act
            line[-1] = pred

    resf = open(resfile, 'w')
    for line in content_list:
        if len(line) == 0:
            resf.write("\n")
        resf.write(' '.join(line) + '\n')
    resf.close()

#######################################################################################

def foliaclass2stanfordtag(e):
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

def folia_sentences2file(inpath, outpath):
    outfile = open(outpath, 'w')
    ids = []
    if os.path.isdir(inpath):
        for filename in os.listdir(inpath):
            doc = folia.Document(file=inpath + '/' + filename)
            for h, sentence in enumerate(doc.sentences()):
                sentence_tokenized = sentence.select(folia.Word)
                words_folia = list(sentence_tokenized)
                word_classes = [w.cls for w in words_folia]
                if 'URL' in word_classes:
                    continue
                for i,word in enumerate(words_folia):
                    w_id = word.id
                    w_text = word.text()
                    if w_id in ids:
                        continue
                    if w_text == '<P>':
                        continue
                    ids.append(w_id)
                    if i + 1 == len(words_folia):
                        outfile.write(w_text + '\n')
                    else:
                        outfile.write(w_text + ' ')
    else:
        print("TODO: Handling of a single Folia file instead of a folder of Folia files.")
    outfile.close()

def folia2sentences(path):
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
                            stf_tag = foliaclass2stanfordtag(entity)
                            actual_stf_tags[_idx] = stf_tag

    else:
        print("TODO: Handling of a single Folia file instead of a folder of Folia files.")
    return [sentences_as_tokens, ids, id2idx, idx2id, all_tokens, actual_stf_tags]


def tag(type, w_nu, prev_tagtype):
    if prev_tagtype is None:
        return 'I-' + type
    else:
        prev_tagtype_splitted = prev_tagtype.split('-')
        if len(prev_tagtype_splitted) <= 1:  # not I-LOC like tag.
            return 'I-' + type
        else:
            prev_type = prev_tagtype_splitted[1]
            if type != prev_type:
                return 'I-' + type
            else:
                if w_nu > 0:
                    return 'I-' + type
                else:
                    return 'B-' + type


def foliaclass2conlltag(e, w_nu, prev_tagtype=None):
    per = 'PER'
    loc = 'LOC'
    org = 'ORG'
    cls = e.cls
    if re.match('^.*Target.*$', e.set):
        if cls == 'name':
            return tag(per, w_nu, prev_tagtype)
    elif re.match('^.*Organizer.*$', e.set):
        if cls == 'name':
            return tag(org, w_nu, prev_tagtype)
    if cls == 'loc' or cls == 'place' or cls == 'place_pub':
        return tag(loc, w_nu, prev_tagtype)
    if cls == 'pname':
        return tag(per, w_nu, prev_tagtype)
    if cls == 'fname':
        return tag(org, w_nu, prev_tagtype)
    return 'O'


def doc2conll(fp, sentences, ids, id2token, id2tag, idx, idx2id, id2idx, id2entityLength, id2entityId, conllfile):

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
            if w_text == '<P>':
                idx = idx - 1
                continue
            sentence_tokens.append(w_id)
            id2token[w_id] = w_text
            id2tag[w_id] = 'O'
            ids.append(w_id)
            idx2id[idx] = w_id
            id2idx[w_id] = idx

            sentences.append(sentence_tokens)
        for layer in sentence.select(folia.EntitiesLayer):
            for entity in layer.select(folia.Entity):
                for w_nu, word in enumerate(entity.wrefs()):
                    word_id = word.id
                    word_idx = id2idx[word_id]
                    word_text = word.text()
                    # Office kelimesi icin overlap durumu var. fname phrase'inin icinde bulunuyor (org). Baska yerde de kendi basina loc olarak isaretlenmis.
                    if word_text == 'satyagraha':
                        print('satyagraha')
                    if word_id == 'https__timesofindia.indiatimes.com_city_bengaluru_He-dares-to-bare-all-for-justice_articleshow_582054535.p.1.s.2.w.36':
                        print('office, which is tagged multiple times.')
                    if word_idx == 0:
                        conll_tagtype = foliaclass2conlltag(entity, w_nu)
                    else:
                        prev_w_idx = word_idx - 1
                        prev_w_id = idx2id[prev_w_idx]
                        prev_tagtype = id2tag[prev_w_id]
                        conll_tagtype = foliaclass2conlltag(entity, w_nu, prev_tagtype)

                    # Asagidaki check'i foliadaki sirali olmayan taglemeler icin yapiyorum. Ornegin ayni id'deki bir entity birden fazla kez taglendiyse
                    # bunlardan biri eger kaydadeger (loc per org vs) ise, o tagi koru. sonradan kaydadeger olmayan bir tagine denk gelsen bile
                    # degistirme. (ornegin 'mosque' kelimesi loc ve religion olarak iki kez taglenmis. Loc olarak tagle. Religion'a geldiginde atla.)

                        prev_tagtype_of_current = id2tag[word_id]
                        if len(conll_tagtype.split('-')) <= 1 : # Su an buldugum tag kaydadeger bir tag degil ise
                            if len(prev_tagtype_of_current.split('-')) <= 1: # daha onceki de kaydadeger degil ise
                                id2tag[word_id] = conll_tagtype
                                id2entityLength[word_id] = len(list(entity.wrefs()))
                                id2entityId[word_id] = entity.id
                        else:
                            if len(prev_tagtype_of_current.split('-')) > 1: # daha onceki de kaydadeger ise
                                # If current entity that the word belongs is longer than the previous entity it belongs,
                                # choose the assign the tag of current entity to the token.
                                parent_entity_length = id2entityLength[word_id]
                                current_entity_length = len(list(entity.wrefs()))
                                if current_entity_length > parent_entity_length:
                                    id2tag[word_id] = conll_tagtype
                                    id2entityLength[word_id] = len(list(entity.wrefs()))
                                    id2entityId[word_id] = entity.id
                                parent_entity_set = id2entityId[word_id]
                                current_entity_set = entity.set
                                if parent_entity_set == current_entity_set:
                                    id2tag[word_id] = conll_tagtype
                                    id2entityLength[word_id] = len(list(entity.wrefs()))
                                    id2entityId[word_id] = entity.id
                                # elif current_entity_length > 1 and parent_entity_length > 1:
                                   # print('An unexpected case: a token in more than one entities of length > 2')
                            else:
                                id2tag[word_id] = conll_tagtype
                                id2entityLength[word_id] = len(list(entity.wrefs()))
                                id2entityId[word_id] = entity.id

        for _id in sentence_tokens:
            line = id2token[_id] + " " + id2tag[_id] + "\n"
            conllfile.write(line)

        conllfile.write("\n")


def folia2conll(flpath, opath):
    id2entityLength = {}
    id2entityId = {}
    sentences = []  # A sentence is a list of token ids.
    ids = []
    id2token = {}
    id2tag = {}
    idx2id = {}
    id2idx = {}
    conll_file = open(opath, 'w')

    idx = -1
    if os.path.isdir(flpath):
        for filename in os.listdir(flpath):
            fpath = flpath + '/' + filename
            doc2conll(fpath, sentences, ids, id2token, id2tag, idx, idx2id, id2idx, id2entityLength, id2entityId, conll_file)
    else:
        doc2conll(flpath, sentences, ids, id2token, id2tag, idx, idx2id, id2idx, conll_file)

    print('Folia docs are converted to conll format')
    conll_file.close()


args = sys.argv

# infile = '../foliadocs/alladjudicated'
# outfile = './foliadocs/alladjudicated/' \
#              'https__timesofindia.indiatimes.com_business_india-business_BSNL-Employees-Union-protests-against-disinvestment_articleshow_972751.folia.xml'

# infile = "/home/berfu/Masaüstü/000_test.txt"
# outfile = "/home/berfu/Masaüstü/000_test_edited.txt"

infile = '../foliadocs/alladjudicated'
outfile = "../foliadocs/foliasentences.txt"

# args = ['utilFormat.py', 'folia2conll', infile, outfile]
# args = ['utilFormat.py', 'conll2raw', infile, outfile]
args = ['utilFormat.py', 'folia_sentences2file', infile, outfile]

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
elif args[1] == 'conll2raw':
    infile = args[2]
    outfile = args[3]
    conll2raw(infile, outfile)
elif args[1] == 'folia2conll':
    infile = args[2]
    outfile = args[3]
    folia2conll(infile, outfile)
elif args[1] == 'folia_sentences2file':
    infile = args[2]
    outfile = args[3]
    folia_sentences2file(infile, outfile)
else:
    print('TODO: change code of other helper functions to allow calling from command prompt.\n')
    sys.exit()