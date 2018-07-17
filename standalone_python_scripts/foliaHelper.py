from pynlpl.formats import folia
import os
import re
import sys


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


def convertFoliaClass2ConllTag(e, w_nu, prev_tagtype=None):
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
                        conll_tagtype = convertFoliaClass2ConllTag(entity, w_nu)
                    else:
                        prev_w_idx = word_idx - 1
                        prev_w_id = idx2id[prev_w_idx]
                        prev_tagtype = id2tag[prev_w_id]
                        conll_tagtype = convertFoliaClass2ConllTag(entity, w_nu, prev_tagtype)

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

folder = '../foliadocs/alladjudicated'
single_file = './foliadocs/alladjudicated/' \
              'https__timesofindia.indiatimes.com_business_india-business_BSNL-Employees-Union-protests-against-disinvestment_articleshow_972751.folia.xml'

args = ['foliaHelper.py', 'folia2conll', folder, './folia_as_conll_test1.txt']
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

