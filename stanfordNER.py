from nltk.tag.stanford import StanfordNERTagger


def runStfModel(sents, tagger, model):
    # Prepare NER tagger with english model
    ner_tagger = StanfordNERTagger(model, tagger, encoding='utf8')
    # Run NER tagger on words
    return ner_tagger.tag_sents(sents)