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

`python stanfordNERTagger.py -nt <ner-tool> -tt <tag-types> -e <eval-metrics> -tf <test-file> -of <out-file>`

An example configuration (Paths are valid from within the project main folder "NERTools")

`python stanfordNERTagger.py -nt stanford -tt 'ORG' 'LOC' 'PER' -e 2 -tf './conll-dataset/test-a.txt' -of './stanford-out-files/out-a.txt'`

If you choose Stanford as NER Tool, the program will want you to specify model and tagger paths.

As an example:

`'./stanford-ner-files/stanford-ner.jar' './stanford-ner-files/ner-model-english-conll-4class.ser.gz'`

### Parameters
- ner-tool: name of the nlp tool you want to use (stanford, spacy, etc.)

- tag-types: Entity tag names. For example it is 'PER' for 'person', 'ORG' for 'organization' and 'LOC' for 'location' entities with respect to [CONLL's 
annotation specifications](http://www.aclweb.org/anthology/W03-0419.pdf) [3].

- eval-metrics: Precision, recall or Matthew's Correlation Coefficient (MCC).

- test-file: Test annotated data file (CONLL2003, ACE, Folia, etc.)

- out-file: Program output in which the scores of the pretrained model are reported.

- tagger-file: the path to the Stanford's tagger file you downloaded earlier on your local.

- model-file: the path to a pretrained model Stanford provided which you downloaded earlier on your local.


### Results

Please see [the Google Docs document](https://docs.google.com/document/d/1wKh2Hzld9ull8IR_dRrcGP6N4TBeJKMxeJllDPkvwGY/edit?usp=sharing) for the results.

### Code

Mostly benefitted from a [blog post](https://blog.sicara.com/train-ner-model-with-nltk-stanford-tagger-english-french-german-6d90573a9486) [4].

## Tool 2: NeuroNER

This package uses Spacy within. It contains a pretrained model, Conll data and a Glove word vector model.

### Installation

- Follow the instructions on [the original page](https://github.com/Franck-Dernoncourt/NeuroNER#requirements)
-- If you already have tensorflow and python3.x, then you do not the script provided. Directly download and unzip NeuroNER:
  `wget https://github.com/Franck-Dernoncourt/NeuroNER/archive/master.zip
sudo apt-get install -y unzip # This line is for Ubuntu users only
unzip master.zip`
- Download the Glove word embeddings. 
`# Download some word embeddings
mkdir NeuroNER-master/data/word_vectors
cd NeuroNER-master/data/word_vectors
wget http://neuroner.com/data/word_vectors/glove.6B.100d.zip
unzip glove.6B.100d.zip`

### Usage

- Open terminal from inside ./src
- Run command:
`python main.py --train_model=False --use_pretrained_model=True --dataset_text_folder=../data/example_unannotated_texts --pretrained_model_folder=../trained_models/conll_2003_en`

### Problem Resolution

Bunch of problems you may encounter and the fixes:

- **ModuleNotFoundError: No module named '\_struct'**:
Ensure you are using the right pyhton on your system. For example in my case it was looking for the module '\_struct' under the wrong python (/usr/local/lib/python). Running the command with the right python (Anaconda's) fixed the issue.

- **ModuleNotFoundError: No module named 'pycorenlp'**:
It is missing in the requirements in the documentation but NeuroNER requires pycorenlp. To install:
`pip install pycorenlp`
Make sure you install it under the right python dist. For example in my case I needed to install it under Anaconda. So I had to run the pip of Anaconda which resides in /anaconda/bin.

-- version: pycorenlp-0.3.0

- **OSError: [E050] Can't find model 'en', ..., AttributeError: 'NeuroNER' object has no attribute 'sess'**:

I got this error with the example command in the **Usage** section above. Could't figure out why. Since we are not very interested in predicting the example_annotaated_texts, I changed the command to:

`python main.py --train_model=False --use_pretrained_model=True --dataset_text_folder=../data/conll_2003/en --pretrained_model_folder=../trained_models/conll_2003_en`

But then I got this error:

- **OSError: For prediction mode, either test set and deploy set must exist in the specified dataset folder: ../data/conll_2003/en**

Configure the arguments 'parameters.ini' with the exact values: 

`train_model = False
use_pretrained_model = True
pretrained_model_folder = ../trained_models/conll_2003_en
dataset_text_folder = ../data/conll2003/en`

A rather hacky solution but it worked.

## Results:

Please see [the Google Docs document](https://docs.google.com/document/d/1wKh2Hzld9ull8IR_dRrcGP6N4TBeJKMxeJllDPkvwGY/edit?usp=sharing) for the results.

## Notes

spacy.py code is yet incomplete. (planned as Tool 2)

The test data and stanford pretrained models used as defaut are available in the project.
You will need to reach The Times of India annotated files by contacting to the team.

## References

[1] [Stanford NER website](https://nlp.stanford.edu/software/CRF-NER.html)

[2] [NLTK’s Stanford NER Library](https://www.nltk.org/_modules/nltk/tag/stanford.html)

[3] Erik F. Tjong Kim Sang and Fien De Meulder. 2003. Introduction to the CoNLL-2003 shared task: Language-independent named entity recognition. In CoNLL-2003. (link)

[4] [Code blog](https://blog.sicara.com/train-ner-model-with-nltk-stanford-tagger-english-french-german-6d90573a9486)

