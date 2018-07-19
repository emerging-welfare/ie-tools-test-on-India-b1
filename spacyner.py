import spacy
from spacy.pipeline import EntityRecognizer
from utilFormat import conll2sentences
from utilFormat import createconllevalinputfile
from utilFormat import conll2raw
from utilEval import runconlleval

# model = 'en_core_web_sm'
model = 'xx_ent_wiki_sm'
nerpath = '/home/berfu/anaconda/lib/python3.6/site-packages/spacy/data/xx_ent_wiki_sm/xx_ent_wiki_sm-2.0.0/ner'
inputfile = 'conll-testb.txt'
outfile = 'spacy_eval'

nlp = spacy.load(model)
[sentences, all_tokens, actual_tags] = conll2sentences(inputfile)

ner = EntityRecognizer(nlp.vocab)
ner.from_disk(nerpath)

result = []
for sentence in sentences:
    doc = spacy.tokens.doc.Doc(nlp.vocab, words=sentence)

    # run ner against every sentence
    processed = ner(doc)
    for token in processed:
        result.append([token.text, token.ent_type_])


print('NER operation ended.')
pred_tags = [t[1] for t in result]
pred_tags_edited = ['O' if x == '' else x for x in pred_tags]
actual_tags_edited = conll2raw(actual_tags)

conlleval_inputfile_name = createconllevalinputfile(sentences, actual_tags_edited, pred_tags_edited)
runconlleval(conlleval_inputfile_name, outfile)




