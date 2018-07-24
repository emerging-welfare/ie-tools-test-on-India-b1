import spacy
from spacy.pipeline import EntityRecognizer

def runspacymodel(sentences, tagger, model):
    # model = 'en_core_web_sm'
    nlp = spacy.load(model)
    ner = EntityRecognizer(nlp.vocab)
    ner.from_disk(tagger)

    result = []
    for sentence in sentences:
        doc = spacy.tokens.doc.Doc(nlp.vocab, words=sentence)

        # run ner against every sentence
        processed = ner(doc)
        for token in processed:
            result.append([token.text, token.ent_type_])
    return  result





