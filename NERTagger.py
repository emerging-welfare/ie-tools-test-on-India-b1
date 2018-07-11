import nltk
import sys
from foliaHelper import readFoliaIntoSentences
from conllHelper import readConllIntoSentences
from metricHelper import findMCC
from metricHelper import findPrecisionRecalls
from stanfordNER import runStfModel
nltk.download('punkt')

args = sys.argv
"""args = ['stanfordNERTagger.py', '-nt', 'stanford',
        '-tt', 'ORG', 'LOC', 'PER', '-e', 1, '-f', 1, '-tf', './conll-dataset/test-a.txt',
        '-of', './stanford-out-files/out-a.txt']"""
ner_tool = 'stanford'
tag_types = ["ORG", "LOC", "PER"]  # no matter what tag is specified, eval for total data is also calculated.
eval_metrics = 0
annotation_format = 1  # Conll: 0, Folia: 1
# testfile = './conll-dataset/test-a.txt'
# outfile = './stanford-out-files/out-a.txt'
testfile = './foliadocs/alladjudicated'
outfile = './stanford-out-files/out-folia.txt'

tagger = './stanford-ner-files/stanford-ner.jar'
model = './stanford-ner-files/ner-model-english-conll-4class.ser.gz'

if len(args) <= 1:
    print("running on default mode \n")
    print("ner tool: StanfordNERTagger \n")
    print("tagtypes: ORG LOC PER \n")
    print("evalmetrics: [0]: precision recall \n")  # [1]: mcc, [2]: precision, recall, mcc.
    print("annotationformat: [0]: Conll \n")
    print("testfile: ./conll-dataset/test-a.txt \n")
    print("outfile: ./stanford-out-files/out-a.txt \n")
    print("tagger: ./stanford-ner-files/stanford-ner.jar \n")
    print("model: ./stanford-ner-files/ner-model-english-conll-4class.ser.gz \n")

else:
    if args[1] == "-h":
        print("Usage \n python3 stanfordNERTagger.py "
              "-t <tagger-file> "
              "-nt <ner-tool>"
              "-e <eval-metrics> "
              "-f <annotation-format>"
              "-tf <test-file> "
              "-of <out-file> | for custom mode \n"
              "If \"StanfordNERTagger\" is selected, as a second step, specify model and tagger with commands: \n"
              "-m <model-file> "
              "-tt <tag-types> \n")
        print("python3 stanfordNERTagger.py | for default mode \n")
        sys.exit()
    else:
        if args[1] != "-nt" or args[3] != "-tt" or args[-8] != "-e" \
                or args[-6] != "-f" or args[-4] != "-tf" or args[-2] != "-of":
            print("Wrong command line arguments. Please type 'python3 stanfordNERTagger.py -h' for help.\n")
        else:
            ner_tool = args[2]
            tag_types = []
            for arg in args[4:-8]:
                tag_types.append(arg)
            eval_metrics = args[-7]
            annotation_format = args[-5]
            testfile = args[-3]
            outfile = args[-1]
            if ner_tool == "stanford":
                print("Now please specify the model and tagger paths (in the order) to use for StanfordNERTagger "
                      "(separate by whitespace): \n")
                tagger_model = input()
                tagger_model = tagger_model.split()
                tagger = tagger_model[0]
                model = tagger_model[1]
            else:
                print("TODO: Implementation for tools other than StanfordNER.")

_sentences = []
actual_stf_tokens = []
actual_stf_tags = []

if annotation_format == 0:  # Conll
    [_sentences, actual_stf_tokens, actual_stf_tags] = readConllIntoSentences(testfile)
elif annotation_format == 1:  # Folia
    [_sentences, ids, id2idx, idx2id, actual_stf_tokens, actual_stf_tags] = readFoliaIntoSentences(testfile)

if ner_tool == 'stanford':
    result = runStfModel(_sentences, tagger, model)
    token_predTag = [item for sublist in result for item in sublist]
else:
    print('TODO: Calling other ner tools.')

"""CALCULATING COMMON VARIABLES"""

pred_stf_tokens = [tp[0] for tp in token_predTag]
pred_stf_tags = [tp[1] for tp in token_predTag]
pred_stf_tags = [tp[1] for tp in token_predTag]

actual = actual_stf_tags
pred = pred_stf_tags

# idx_act_pred_same = [(i,actual_stf_tokens[i], actual[i],pred[i]) for i in range(len(pred))
# if actual[i] == pred[i] and actual[i] != O]

# all fp and fn including 'other'
idx_token_act_pred_diff = [(i,actual_stf_tokens[i], actual[i],pred[i]) for i in range(len(pred)) if actual[i] != pred[i]]
# all fp and fn including 'other'
idx_diff = [i[0] for i in idx_token_act_pred_diff]
# tp except 'other'
idx_tag_numerator = [(i,actual_stf_tokens[i], actual[i], pred[i]) for i in range(len(pred)) if i not in idx_diff and actual[i] != 'O']

"""START CODE FOR SCORING"""

# Calculate Precision and Recall for tags individually, or MCC, depending on the arguments.
if eval_metrics == 0:
    tag2precrec = findPrecisionRecalls(actual_stf_tokens, actual,pred, idx_diff, tag_types)
elif eval_metrics == 1:
    mcc = findMCC(idx_tag_numerator, idx_token_act_pred_diff, idx_diff, actual, pred)
elif eval_metrics == 2:
    tag2precrec = findPrecisionRecalls(actual_stf_tokens, actual,pred, idx_diff, tag_types)
    mcc = findMCC(idx_tag_numerator, idx_token_act_pred_diff, idx_diff, actual, pred)


# Write scores to file
scores_file = open(outfile,'w')
scores_file.write("Scores: \n")
scores_file.write("(Type 'other' results are omitted before calculating scores other than MCC.) \n")
if eval_metrics != 0:
    scores_file.write("Matthew's Correlation Coefficient: "+ str(round(mcc, 2)) + "\n\n")

if eval_metrics != 1:
    for t in tag2precrec.keys():
        scores_file.write(t + " precision: " + str(round(tag2precrec[t][0], 2)) + "\n")
        scores_file.write(t + " recall: " + str(round(tag2precrec[t][1], 2)) + "\n\n")

scores_file.close()

"""END CODE FOR SCORING"""














