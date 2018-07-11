import math


def findPrecisionRecalls(actual_stf_tokens, actual,pred, idx_diff, tag_types):
    tag2scores = {}
    # tp for 'loc'
    idx_tag_numerator_loc = [(i, actual[i], pred[i]) for i in range(len(pred)) if
                             i not in idx_diff and actual[i] == 'LOCATION']
    idx_tag_act_loc = [(i, actual[i], pred[i]) for i in range(len(pred)) if actual[i] == 'LOCATION']
    idx_tag_pred_loc = [(i, actual[i], pred[i]) for i in range(len(pred)) if pred[i] == 'LOCATION']

    """EXAMINE RESULTS FOR LOC"""
    actual_locs_missed = [[actual_stf_tokens[a[0]], a] for a in idx_tag_act_loc if pred[a[0]] != 'LOCATION']  # 558, nearly all of them has lower-cased first letters.
    actual_locs_catched = [[actual_stf_tokens[a[0]], a] for a in idx_tag_act_loc if pred[a[0]] == 'LOCATION']  # 17. All of them start with upper-cased letters.

    # tp for 'per'
    idx_tag_numerator_per = [(i, actual[i], pred[i]) for i in range(len(pred)) if
                             i not in idx_diff and actual[i] == 'PERSON']
    idx_tag_act_per = [(i, actual[i], pred[i]) for i in range(len(pred)) if actual[i] == 'PERSON']
    idx_tag_pred_per = [(i, actual[i], pred[i]) for i in range(len(pred)) if pred[i] == 'PERSON']

    """EXAMINE RESULTS FOR PER"""
    actual_pers_missed = [[actual_stf_tokens[a[0]], a] for a in idx_tag_act_per if
                          pred[a[0]] != 'PERSON']  # 558, nearly all of them has lower-cased first letters.
    actual_pers_catched = [[actual_stf_tokens[a[0]], a] for a in idx_tag_act_per if
                           pred[a[0]] == 'PERSON']  # 17. All of them start with upper-cased letters.

    # tp for 'org'
    idx_tag_numerator_org = [(i, actual[i], pred[i]) for i in range(len(pred)) if
                             i not in idx_diff and actual[i] == 'ORGANIZATION']
    idx_tag_act_org = [(i, actual[i], pred[i]) for i in range(len(pred)) if actual[i] == 'ORGANIZATION']
    idx_tag_pred_org = [(i, actual[i], pred[i]) for i in range(len(pred)) if pred[i] == 'ORGANIZATION']

    """EXAMINE RESULTS FOR ORG"""
    actual_orgs_missed = [[actual_stf_tokens[a[0]], a] for a in idx_tag_act_org if
                          pred[a[0]] != 'ORGANIZATION']  # 558, nearly all of them has lower-cased first letters.
    actual_orgs_catched = [[actual_stf_tokens[a[0]], a] for a in idx_tag_act_org if
                           pred[a[0]] == 'ORGANIZATION']  # 17. All of them start with upper-cased letters.

    total_numerator = len(idx_tag_numerator_loc) + len(idx_tag_numerator_per) + len(idx_tag_numerator_org)
    total_recall = total_numerator / (len(idx_tag_act_loc) + len(idx_tag_act_per) + len(idx_tag_act_org))
    total_prec = total_numerator / (len(idx_tag_pred_loc) + len(idx_tag_pred_per) + len(idx_tag_pred_org))
    tag2scores['TOTAL'] = [total_prec,total_recall]

    if "LOC" in tag_types:
        loc_recall = len(idx_tag_numerator_loc) / len(idx_tag_act_loc)
        loc_prec = len(idx_tag_numerator_loc) / len(idx_tag_pred_loc)
        tag2scores['LOC'] = [loc_prec, loc_recall]
    if "PER" in tag_types:
        per_recall = len(idx_tag_numerator_per) / len(idx_tag_act_per)
        per_prec = len(idx_tag_numerator_per) / len(idx_tag_pred_per)
        tag2scores['PER'] = [per_prec, per_recall]
    if "ORG" in tag_types:
        org_recall = len(idx_tag_numerator_org) / len(idx_tag_act_org)
        org_prec = len(idx_tag_numerator_org) / len(idx_tag_pred_org)
        tag2scores['ORG'] = [org_prec, org_recall]

    return tag2scores


def findMCC(idx_tag_numerator, idx_act_pred_diff, idx_diff, actual, pred):
    # tp for 'loc'
    idx_tag_numerator_loc = [(i, actual[i], pred[i]) for i in range(len(pred)) if
                             i not in idx_diff and actual[i] == 'LOCATION']
    # tp for 'per'
    idx_tag_numerator_per = [(i, actual[i], pred[i]) for i in range(len(pred)) if
                             i not in idx_diff and actual[i] == 'PERSON']
    # tp for 'org'
    idx_tag_numerator_org = [(i, actual[i], pred[i]) for i in range(len(pred)) if
                             i not in idx_diff and actual[i] == 'ORGANIZATION']

    total_tp = idx_tag_numerator
    # fp_for loc
    # itd[0] corresponds to the 'id' column of the element in the idx_tag_diff list.
    fp_loc = [itd[0]
              for itd in idx_act_pred_diff if itd[2] == 'LOCATION']

    # fn for loc
    fn_loc = [itd[0]
              for itd in idx_act_pred_diff if itd[1] == 'LOCATION']

    # fp_for per
    fp_per = [itd[0]
              for itd in idx_act_pred_diff if itd[2] == 'PERSON']

    # fn for per
    fn_per = [itd[0]
              for itd in idx_act_pred_diff if itd[1] == 'PERSON']

    # fp_for org
    fp_org = [itd[0]
              for itd in idx_act_pred_diff if itd[2] == 'ORGANIZATION']

    # fn for org
    fn_org = [itd[0]
              for itd in idx_act_pred_diff if itd[1] == 'ORGANIZATION']

    # tn for loc
    tn_loc = [i for i in range(len(pred)) if i not in idx_diff and actual[i] != 'LOCATION']

    # tn for per
    tn_per = [i for i in range(len(pred)) if i not in idx_diff and actual[i] != 'PERSON']
    # tn for org
    tn_org = [i for i in range(len(pred)) if i not in idx_diff and actual[i] != 'ORGANIZATION']

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

    return MCC_numerator / MCC_denominator