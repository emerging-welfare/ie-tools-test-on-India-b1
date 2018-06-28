import nltk
from nltk.tag.stanford import StanfordNERTagger
nltk.download('punkt')
import re
import math

jar = './stanford-ner-tagger/stanford-ner.jar'
model = './stanford-ner-tagger/ner-model-english-conll-4class.ser.gz'

# Prepare NER tagger with english model
ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

lines= []
sentences = [[]]
with open('./conll-dataset/testb.txt','r') as f:
    for line in f:
        if line != '\n':
            sentences[-1].append(line.split(None, 1)[0])
            lines.append(line.split())
        else:
            sentences.append([])

token_actualTag = [(line[0], line[-1]) for line in lines]
token_actualTag = [(line[0], 'LOCATION') if re.match('^.*LOC.*$', line[-1])
                   else (line[0], line[-1]) for line in lines]

token_actualTag = [(line[0], 'PERSON') if re.match('^.*PER.*$', line[-1])
                   else (line[0], line[-1]) for line in token_actualTag]

token_actualTag = [(line[0], 'ORGANIZATION') if re.match('^.*ORG.*$', line[-1])
                   else (line[0], line[-1]) for line in token_actualTag]

token_actualTag = [(line[0], 'O') if re.match('^.*MISC.*$', line[-1])
                   else (line[0], line[-1]) for line in token_actualTag]

"""
token_actualTag = [(line[0], 'PERSON') for line in lines if re.match('^.*PER.*$', line[-1])]
token_actualTag = [(line[0], 'ORGANIZATION') for line in lines if re.match('^.*ORG.*$', line[-1])]
"""
"""
test_locs = [i for i in test_data if i[3] == 'I-LOC']
num_locs = len(test_locs)
locs = [[i[0], i[-1]] for i in test_locs]
"""

# Run NER tagger on words
result = ner_tagger.tag_sents(sentences)
token_predTag = [item for sublist in result for item in sublist]

# Calculate precision, recall for tags (LOC, PER, ORG), both together and separate.

actual = [ta[1] for ta in token_actualTag]
pred = [tp[1] for tp in token_predTag]
#all fp and fn including 'other'
idx_tag_diff = [(i,token_actualTag[i][0],actual[i],pred[i]) for i in range(len(pred)) if actual[i] != pred[i]]

# total_accuracy = 1 - len(idx_tag_diff)/len(actual)
#all fp and fn including 'other'
idx = [i[0] for i in idx_tag_diff]

# tp except 'other'
idx_tag_numerator = [(i,actual[i],pred[i]) for i in range(len(pred)) if i not in idx and actual[i] != 'O']
# tp_loc + tp_per + tp_org + fp_loc + fp_per + fp_org
idx_tag_pred = [(i,actual[i],pred[i]) for i in range(len(pred)) if pred[i] != 'O']
# Microaveraging the precision
total_prec = len(idx_tag_numerator)/len(idx_tag_pred)

# tp_loc + tp_per + tp_org + fn_loc + fn_per + fn_org
idx_tag_act = [(i,actual[i],pred[i]) for i in range(len(pred)) if actual[i] != 'O']
# Microaveraging the recall
total_recall = len(idx_tag_numerator)/len(idx_tag_act)

# tp for 'loc'
idx_tag_numerator_loc = [(i,actual[i],pred[i]) for i in range(len(pred)) if i not in idx and actual[i] == 'LOCATION']
# tp for 'per'
idx_tag_numerator_per = [(i,actual[i],pred[i]) for i in range(len(pred)) if i not in idx and actual[i] == 'PERSON']
# tp for 'org'
idx_tag_numerator_org = [(i,actual[i],pred[i]) for i in range(len(pred)) if i not in idx and actual[i] == 'ORGANIZATION']

idx_tag_act_loc = [(i,actual[i],pred[i]) for i in range(len(pred)) if actual[i] == 'LOCATION']
idx_tag_act_per = [(i,actual[i],pred[i]) for i in range(len(pred)) if actual[i] == 'PERSON']
idx_tag_act_org = [(i,actual[i],pred[i]) for i in range(len(pred)) if actual[i] == 'ORGANIZATION']

loc_prec = len(idx_tag_numerator_loc)/len(idx_tag_act_loc)
per_prec = len(idx_tag_numerator_per)/len(idx_tag_act_per)
org_prec = len(idx_tag_numerator_org)/len(idx_tag_act_org)

idx_tag_pred_loc = [(i,actual[i],pred[i]) for i in range(len(pred)) if pred[i] == 'LOCATION']
idx_tag_pred_per = [(i,actual[i],pred[i]) for i in range(len(pred)) if pred[i] == 'PERSON']
idx_tag_pred_org = [(i,actual[i],pred[i]) for i in range(len(pred)) if pred[i] == 'ORGANIZATION']

loc_recall = len(idx_tag_numerator_loc)/len(idx_tag_pred_loc)
per_recall = len(idx_tag_numerator_per)/len(idx_tag_pred_per)
org_recall = len(idx_tag_numerator_org)/len(idx_tag_pred_org)

# Calculate MCC score for the whole dataset (without omitting the tokens 'other' than LOC,PER and ORG.
total_tp = idx_tag_numerator
#fp_for loc
# itd[0] corresponds to the 'id' column of the element in the idx_tag_diff list.
fp_loc = [itd[0]
                    for itd in idx_tag_diff if itd[3] == 'LOCATION']

#fn for loc
fn_loc = [itd[0]
                    for itd in idx_tag_diff if itd[2] == 'LOCATION']

#fp_for per
fp_per = [itd[0]
                    for itd in idx_tag_diff if itd[3] == 'PERSON']

#fn for per
fn_per = [itd[0]
                    for itd in idx_tag_diff if itd[2] == 'PERSON']

#fp_for org
fp_org = [itd[0]
                    for itd in idx_tag_diff if itd[3] == 'ORGANIZATION']

#fn for org
fn_org = [itd[0]
                    for itd in idx_tag_diff if itd[2] == 'ORGANIZATION']

#tn for loc
tn_loc = [i for i in range(len(pred)) if i not in idx and actual[i] != 'LOCATION']

#tn for per
tn_per = [i for i in range(len(pred)) if i not in idx and actual[i] != 'PERSON']
#tn for org
tn_org = [i for i in range(len(pred)) if i not in idx and actual[i] != 'ORGANIZATION']

tp_loc = idx_tag_numerator_loc
tp_per = idx_tag_numerator_per
tp_org = idx_tag_numerator_org
total_tp = len(tp_loc) + len(tp_per) + len(tp_org)
total_tn = len(tn_loc) + len(tn_per) + len(tn_org)
total_fp = len(fp_loc) + len(fp_per) + len(fp_org)
total_fn = len(fn_loc) + len(fn_per) + len(fn_org)

total_pred_p = total_tp + total_fp
total_pred_n = total_tn + total_fn
total_actual_n = total_fp + total_tn
total_actual_p = total_tp + total_fn

MCC_numerator = total_tp * total_tn - total_fp * total_fn
MCC_denominator = math.sqrt(total_pred_p * total_pred_n * total_actual_p * total_actual_n)
MCC = MCC_numerator / MCC_denominator

# Write scores to file
scores_file = open('./testb_scores.txt','w')
scores_file.write("Scores for 'testb': \n")
scores_file.write("(Type 'other' results are omitted before calculating scores below.) \n")
scores_file.write("Total precision: " + str(round(total_prec,2)) + "\n")
scores_file.write("Total recall: " + str(round(total_recall,2)) + "\n\n")
scores_file.write("Location precision: " + str(round(loc_prec,2)) + "\n")
scores_file.write("Location recall: " + str(round(loc_recall,2)) + "\n\n")
scores_file.write("Person precision: "+ str(round(per_prec,2))+ "\n")
scores_file.write("Person recall: "+ str(round(per_recall,2))+ "\n\n")
scores_file.write("Organization precision: "+ str(round(org_prec,2))+ "\n")
scores_file.write("Organization recall: "+ str(round(org_recall,2))+ "\n\n")
scores_file.write("Matthew's Correlation Coefficient: "+ str(round(MCC, 2))+ "\n\n")
scores_file.close()














