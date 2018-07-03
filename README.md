# NERTools
This repo consists of scripts to test existing named-entity recognition tools (such as StanfordNER, Spacy, ...) 
in order to determine baseline models for EMW project in Koc University, Istanbul.

## Tool 1: StanfordNER

StanfordNER is a widely used extensive NLP library. This script tests a pretrained Stanford NER classifier to several news datasets,
namely, CONLL2003; Folia and ACE.

The script simply takes a **pretrained model** and an **input text** as input, gives a **scores** file as output. 

### Requirements

- Python3.x.x (my version is 3.6.3), 
- [Stanford's pretrained classifiers 3.9.1](https://nlp.stanford.edu/software/CRF-NER.html) [1], 
- [NLTK's Stanford NER library 3.2.4](https://www.nltk.org/_modules/nltk/tag/stanford.html) [2].

### Usage
The script allows two types of configurations: **default** and **custom** mode.

To run on default mode, type:

`python stanfordNERTagger.py`

To run on custom mode, you should specify the parameters in the order below:

`python stanfordNERTagger.py -t <tagger-file> -m <model-file> -tt <tag-types> -e <eval-metrics> -tf <test-file> -of <out-file>`

An example configuration (Paths are valid from within the project main folder "NERTools")

`python stanfordNERTagger.py -t './stanford-ner-files/stanford-ner.jar' -m './stanford-ner-files/ner-model-english-conll-4class.ser.gz' -tt 'ORG' 'LOC' 'PER' -e 2 -tf './conll-dataset/test-a.txt' -of './stanford-out-files/out-a.txt'`

### Parameters

- tagger-file: the path to the Stanford's tagger file you downloaded earlier on your local.

- model-file: the path to a pretrained model Stanford provided which you downloaded earlier on your local.

- tag-types: Entity tag names. For example it is 'PER' for 'person', 'ORG' for 'organization' and 'LOC' for 'location' entities with respect to [CONLL's 
annotation specifications](http://www.aclweb.org/anthology/W03-0419.pdf) [3].

- eval-metrics: Precision, recall or Matthew's Correlation Coefficient (MCC).

- test-file: Test annotated data file (CONLL2003, ACE, Folia, etc.)

- out-file: Program output in which the scores of the pretrained model are reported.

### Results

Please see [the Google Docs document](https://docs.google.com/document/d/1wKh2Hzld9ull8IR_dRrcGP6N4TBeJKMxeJllDPkvwGY/edit?usp=sharing) for the results.

### Code

Mostly benefitted from a [blog post](https://blog.sicara.com/train-ner-model-with-nltk-stanford-tagger-english-french-german-6d90573a9486) [4].

## Notes

spacy.py code is yet incomplete. (planned as Tool 2)

## References
[1] [Stanford NER website](https://nlp.stanford.edu/software/CRF-NER.html)

[2] [NLTK’s Stanford NER Library](https://www.nltk.org/_modules/nltk/tag/stanford.html)

[3] Erik F. Tjong Kim Sang and Fien De Meulder. 2003. Introduction to the CoNLL-2003 shared task: Language-independent named entity recognition. In CoNLL-2003. (link)

[4] [Code blog](https://blog.sicara.com/train-ner-model-with-nltk-stanford-tagger-english-french-german-6d90573a9486)

