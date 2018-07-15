# clear tags from initial parts (I-LOC to LOC, etc)
# I required this operation to evaluate NeuroNER prediction results on folia docs.
# The reason is that the predictor outputs conll formatted tags such as I-LOC, B-LOC.
# However, for folia docs I do  not have information about tag initials.
# Since NeuroNER accepts decent conll formatted test files as output, I had to assign initials to tags.
# And I arbitrarily assigned I, at the beginning of each tag - except for O and MISC.


# Now after prediction, default conlleval evaluates the results regarding the initials as well as the tags.
# This brings an additional error to the results.
# So for better understanding, with this code I omit the initials for both the actual and predicted tags.
# Conlleval has also an option named -r. It assumes the tags are "raw': initial-free.

def omit_initials_from_tags(outfile, resfile):
    with open(outfile) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        content_list = [x.split() for x in content]

        for line in content_list:
            if len(line) == 0:
                continue
            act = line[-2]
            pred = line[-1]
            
            a = act.split('-')
            p = pred.split('-')

            if len(a) > 1: act = a[1]
            if len(p) > 1: pred = p[1]
            line[-2] = act
            line[-1] = pred

    resf = open(resfile, 'w')
    for line in content_list:
        if len(line) == 0:
            resf.write("\n")
        resf.write(' '.join(line) + '\n')
    resf.close()
    

out =  "./000_test.txt"
res =  "./000_test_edited.txt"
omit_initials_from_tags(out, res)
