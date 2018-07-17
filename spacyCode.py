import spacy
# from spacy.pipeline import EntityRecognizer
from conllHelper import readConllIntoSentences

sentences = readConllIntoSentences('./conll-dataset/test-b.txt')[0]


# nlp = spacy.load('./xx_ent_wiki_sm/xx_ent_wiki_sm-2.0.0')
nlp = spacy.load('./spacy-models/xx_ent_wiki_sm/xx_ent_wiki_sm-2.0.0')
#tagger = Tagger(nlp.vocab)

# ner = EntityRecognizer(nlp.vocab)
# ner.from_disk('./xx_ent_wiki_sm/xx_ent_wiki_sm-2.0.0/ner')
ner = nlp.ner
# doc = nlp(u"This is a sentence.")
# processed = ner(doc)
# tagger(doc)

result = []
for sentence in sentences:
    doc = spacy.tokens.doc.Doc(nlp.vocab, words=sentence)

    # run ner against every sentence
    processed = ner(doc)
    res = nlp(processed.text)
    for token in res:
        print(token.text, token.ent_type_)
        result.append([token.text, token.ent_type_])

"""
result = []
for sentence in sentences:
    doc = spacy.tokens.doc.Doc(nlp.vocab, words=sentence)

    # run the standard pipeline against it
    for name, proc in nlp.pipeline:
        doc = proc(doc)
        res = nlp(doc.text)
        for token in res:
            print(token.text, token.ent_type_)
            result.append([token.text, token.ent_type_])

print("Operation ended.")
sample_file = open('./testb_sample_scores_spacy.txt','w')
for i in range(300):
    sample_file.write(str(result[i]) + "\n")
sample_file.close()
"""



