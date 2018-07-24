import nltk
import sys
from utilFormat import folia2sentences
from utilFormat import conll2sentences
from utilEval import runconlleval
from stanfordner import runstanfordmodel
from spacyner import runspacymodel
from utilFormat import conll2stanford
from utilFormat import conll2raw
from utilFormat import stanford2raw
from utilFormat import createconllevalinputfile
nltk.download('punkt')

args = sys.argv
"""args = ['tagger.py', 
            'stanford',
            'conll', 
            'conll-testa.txt',
            'conll-testa-out.txt']"""

ner_tool = 'spacy' # stanford, spacy
annotation_format = 'folia'  # conll, folia
testfile = './foliadocs/alladjudicated'
outfile = 'folia-out.txt'
model = 'xx_ent_wiki_sm'
tagger = '/home/berfu/anaconda/lib/python3.6/site-packages/spacy/data/xx_ent_wiki_sm/xx_ent_wiki_sm-2.0.0/ner'
# tagger = 'stanford-ner.jar'
# model = 'stanford-en-4class.ser.gz'
# testfile = 'conll-testa.txt'
# outfile = 'conll-testa-out.txt'

if len(args) <= 1:
    print("running on default mode \n")
    print("ner tool: " + ner_tool + "\n")
    print("annotationformat: " + annotation_format + "\n")
    print("testfile: " + testfile + "\n")
    print("outfile: " + outfile + "\n")
    print("tagger: " + tagger + "\n")
    print("model: " + model + "\n")

else:
    if args[1] == "-h":
        print("Usage \n python3 tagger.py "
              "<ner-tool>"
              "<annotation-format>"
              "<test-file> "
              "<out-file> | for custom mode \n"
              "If \"stanford\" is selected as the tool, as a second step, specify model and tagger with commands: \n"
              "<model-file> "
              "<tag-types> \n")
        print("python3 tagger.py | for default mode \n")
        sys.exit()
    else:
        if len(args) != 5:
            print("Wrong command line arguments. Please type 'python3 tagger.py -h' for help.\n")
        else:
            ner_tool = args[2]
            annotation_format = args[-5]
            testfile = args[-3]
            outfile = args[-1]
            if ner_tool == "stanford":
                print("Now please specify the model and tagger paths to be used, respectively: "
                      "(separate by whitespace): \n")
                tagger_model = input()
                tagger_model = tagger_model.split()
                tagger = tagger_model[0]
                model = tagger_model[1]
            elif ner_tool == 'spacy':
                print("Now please specify the model and ner paths to be used, respectively: "
                      "(separate by whitespace): \n")
                tagger_model = input()
                tagger_model = tagger_model.split()
                tagger = tagger_model[0]
                model = tagger_model[1]

_sentences = []
actual_tags = []

if annotation_format == 'conll':
    [_sentences, tokens, actual_tags] = conll2sentences(testfile)
    if ner_tool == 'stanford':
        actual_tags = conll2stanford(actual_tags)
    elif ner_tool == 'spacy':
        actual_tags = conll2raw(actual_tags)
elif annotation_format == 'folia':
    if ner_tool == 'stanford':
        [_sentences, tokens, actual_tags] = folia2sentences(testfile, 'stanford')
    elif ner_tool == 'spacy':
        [_sentences, tokens, actual_tags] = folia2sentences(testfile, 'raw')


if ner_tool == 'stanford':
    result = runstanfordmodel(_sentences, tagger, model)
    token_predTag = [item for sublist in result for item in sublist]
    actual_tags = stanford2raw(actual_tags)
    pred_tags = [tp[1] for tp in token_predTag]
    pred_tags_edited = stanford2raw(pred_tags)

elif ner_tool == 'spacy':
    result = runspacymodel(_sentences, tagger, model)
    pred_tags = [t[1] for t in result]
    pred_tags_edited = ['O' if x == '' else x for x in pred_tags]
    if annotation_format == 'conll':
        actual_tags = conll2raw(actual_tags)

# Run conlleval script
conlleval_inputfile_name = createconllevalinputfile(_sentences, actual_tags, pred_tags_edited)
runconlleval(conlleval_inputfile_name, outfile)
print('Operation ended.\n')












