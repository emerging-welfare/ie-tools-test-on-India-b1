import re
from pynlpl.formats import folia
import os

# returns object
def conll2raw(tags):
    raw_tags = []
    for tag in tags:
        raw_tag = tag
        t = tag.split('-')
        if len(t) > 1: raw_tag = t[1]
        raw_tags.append(raw_tag)
    return raw_tags

# returns object
def stanford2raw(tags):
    tags = ['LOC' if tag == 'LOCATION'
                       else tag for tag in tags]

    tags = ['PER' if tag == 'PERSON'
           else tag for tag in tags]

    tags = ['ORG' if tag == 'ORGANIZATION'
                       else tag for tag in tags]
    return tags

# returns object
def conll2stanford(tags):
    tags = ['LOCATION' if re.match('^.*LOC.*$', tag)
                       else tag for tag in tags]

    tags = ['PERSON' if re.match('^.*PER.*$', tag)
                       else tag for tag in tags]

    tags = ['ORGANIZATION' if re.match('^.*ORG.*$', tag)
                       else tag for tag in tags]
    return tags

# returns objects
def conll2sentences(testfile):
    with open(testfile, 'r') as f:
        lines = []
        sentences = [[]]
        for line in f:
            if line != '\n':
                sentences[-1].append(line.split(None, 1)[0])
                lines.append(line.split())
            else:
                sentences.append([])
    all_tokens = [line[0] for line in lines]
    actual_tags = [line[-1] for line in lines]
    return [sentences, all_tokens, actual_tags]

# returns created file's name
def createconllevalinputfile(sentences, actual_tags, pred_tags):
    conlleval_inputfile_name = 'conlleval_input'
    result_file = open(conlleval_inputfile_name, 'w')
    idx = -1
    for sentence in sentences:
        for word in sentence:
            idx = idx + 1
            result_file.write(word + ' ' + actual_tags[idx] + ' ' + pred_tags[idx] + '\n')
        result_file.write('\n')
    result_file.close()
    return conlleval_inputfile_name

#################################################################################################
# intermediate func
def foliaclass2rawtag(e):
    per = 'PER'
    loc = 'LOC'
    org = 'ORG'
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

# intermediate func
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

# returns objects
def folia2sentences(path, tagFormat):
    sentences_as_tokens = []
    ids = []
    id2idx = {}
    idx2id = {}
    all_tokens = []
    actual_tags = []
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
                    if w_text == '<P>':
                        idx = idx - 1
                        continue
                    if w_text == 'krishnappa':
                        idx = idx - 1
                        continue
                    ids.append(w_id)
                    id2idx[w_id] = idx
                    idx2id[idx] = w_id
                    actual_tags.append('O')
                    sentence_tokens.append(w_text)
                    all_tokens.append(w_text)

                sentences_as_tokens.append(sentence_tokens)
                for layer in sentence.select(folia.EntitiesLayer):
                    for entity in layer.select(folia.Entity):
                        for word in entity.wrefs():
                            word_id = word.id
                            _idx = id2idx[word_id]
                            if tagFormat == 'stanford':
                                tag = foliaclass2stanfordtag(entity)
                            elif tagFormat == 'conll':
                                print('TODO: reuse codes that output files to output objects instead.')
                            elif tagFormat == 'raw':
                                tag = foliaclass2rawtag(entity)
                            actual_tags[_idx] = tag

    else:
        print("TODO: Handling of a single Folia file instead of a folder of Folia files.")
    return [sentences_as_tokens, all_tokens, actual_tags]

#intermediate func
def tag(type, w_nu, prev_type):
    if prev_type is None:
        return 'I-' + type
    else:
        if prev_type not in ['LOC', 'ORG', 'PER']:
            return 'I-' + type
        else:
            if type != prev_type:
                return 'I-' + type
            else:
                if w_nu > 0:
                    return 'I-' + type
                else:
                    return 'B-' + type

# intermediate func
def foliaclass2conlltag(e, w_nu, prev_type=None):
    per = 'PER'
    loc = 'LOC'
    org = 'ORG'
    cls = e.cls
    if re.match('^.*Target.*$', e.set):
        if cls == 'name':
            return tag(per, w_nu, prev_type)
    elif re.match('^.*Organizer.*$', e.set):
        if cls == 'name':
            return tag(org, w_nu, prev_type)
    if cls == 'loc' or cls == 'place' or cls == 'place_pub':
        return tag(loc, w_nu, prev_type)
    if cls == 'pname':
        return tag(per, w_nu, prev_type)
    if cls == 'fname':
        return tag(org, w_nu, prev_type)
    return 'O'

# intermediate func
def doc2conll(fp, sentences, ids, id2token, id2tag, idx, idx2id, id2idx, conllfile):

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
                    if len(id2tag.keys()) == 0:
                        conll_tag = foliaclass2conlltag(entity, w_nu)
                    else:
                        prev_w_idx = id2idx[word_id] - 1
                        prev_w_id = idx2id[prev_w_idx]
                        prev_type = id2tag[prev_w_id]
                        conll_tag = foliaclass2conlltag(entity, w_nu, prev_type)
                    id2tag[word_id] = conll_tag

        for _id in sentence_tokens:
            line = id2token[_id] + " " + id2tag[_id] + "\n"
            conllfile.write(line)

        conllfile.write("\n")


# returns nothing
def folia2conll(flpath, opath):
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
            doc2conll(fpath, sentences, ids, id2token, id2tag, idx, idx2id, id2idx, conll_file)
    else:
        doc2conll(flpath, sentences, ids, id2token, id2tag, idx, idx2id, id2idx, conll_file)

    print('Folia docs are converted to conll format')
    conll_file.close()



