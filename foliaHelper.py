from pynlpl.formats import folia
import os
import re


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

"""
pred_idx = [i for i,e in enumerate(pred_stf_tags) if (e != 'O' and e != 'MISC')]
pred_ids_non_misc = [idx2id[i] for i in pred_idx]
pred_tokens_non_misc = [pred_stf_tokens[i] for i in pred_idx]
pred_tags_non_misc = [pred_stf_tags[i] for i in pred_idx]
pred_token_tag_non_misc = [[pred_tokens_non_misc[i], pred_tags_non_misc[i]] for i in range(len(pred_tokens_non_misc))]
pred_id_tag_non_misc = [[pred_ids_non_misc[i], pred_tags_non_misc[i]] for i in range(len(pred_tokens_non_misc))]

actual_idx = [i for i,e in enumerate(actual_stf_tags) if e != 'O']
actual_ids_non_misc = [idx2id[i] for i in actual_idx]
actual_tokens_non_misc = [all_tokens[i] for i in actual_idx]
actual_tags_non_misc = [actual_stf_tags[i] for i in actual_idx]
actual_token_tag_non_misc = [[actual_tokens_non_misc[i], actual_tags_non_misc[i]] for i in range(len(actual_tokens_non_misc))]
actual_id_tag_non_misc = [[actual_ids_non_misc[i], actual_tags_non_misc[i]] for i in range(len(actual_tokens_non_misc))]
"""


"""START CODE FOR FOLIA SCORING"""
"""
pred_idx = [i for i,e in enumerate(pred_stf_tags) if (e != 'O' and e != 'MISC')]
actual_idx = [i for i,e in enumerate(actual_stf_tags) if e != 'O']

pred_idx_true_loc = [i for i,e in enumerate(pred_stf_tags) if e == 'LOCATION' and actual_stf_tags[i] == 'LOCATION']
actual_idx_loc = [i for i,e in enumerate(actual_stf_tags) if e == 'LOCATION']
pred_idx_loc = [i for i,e in enumerate(pred_stf_tags) if e == 'LOCATION']

prec_loc = len(pred_idx_true_loc)/len(pred_idx_loc)

pred_idx_true_per = [i for i,e in enumerate(pred_stf_tags) if e == 'PERSON' and actual_stf_tags[i] == 'PERSON']
actual_idx_per = [i for i,e in enumerate(actual_stf_tags) if e == 'PERSON']
pred_idx_per = [i for i,e in enumerate(pred_stf_tags) if e == 'PERSON']

prec_per = len(pred_idx_true_per)/len(pred_idx_per)

pred_idx_true_org = [i for i,e in enumerate(pred_stf_tags) if e == 'ORGANIZATION' and actual_stf_tags[i] == 'ORGANIZATION']
actual_idx_org = [i for i,e in enumerate(actual_stf_tags) if e == 'ORGANIZATION']
pred_idx_org = [i for i,e in enumerate(pred_stf_tags) if e == 'ORGANIZATION']

prec_org = len(pred_idx_true_org)/len(pred_idx_org)

actual_idx_loc = [i for i,e in enumerate(actual_stf_tags) if e == 'LOCATION']
rec_loc = len(pred_idx_true_loc)/len(actual_idx_loc)

actual_idx_per = [i for i,e in enumerate(actual_stf_tags) if e == 'PERSON']
rec_per = len(pred_idx_true_per)/len(actual_idx_per)

actual_idx_org = [i for i,e in enumerate(actual_stf_tags) if e == 'ORGANIZATION']
rec_org = len(pred_idx_true_org)/len(actual_idx_org)

prec_total = (len(pred_idx_true_loc) + len(pred_idx_true_per) + len(pred_idx_true_org)) / len(pred_idx)
rec_total = (len(pred_idx_true_loc) + len(pred_idx_true_per) + len(pred_idx_true_org)) / len(actual_idx)
"""
"""END CODE FOR FOLIA SCORING"""
