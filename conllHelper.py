import re


def readConllIntoSentences(testfile):
    with open(testfile, 'r') as f:
        lines = []
        sentences = [[]]
        for line in f:
            if line != '\n':
                sentences[-1].append(line.split(None, 1)[0])
                lines.append(line.split())
            else:
                sentences.append([])
    all_tokens = [line[0] for line in lines]
    actual_tags = [line[-1] for line in lines]
    actual_tags = ['LOCATION' if re.match('^.*LOC.*$', tag)
                       else tag for tag in actual_tags]

    actual_tags = ['PERSON' if re.match('^.*PER.*$', tag)
                       else tag for tag in actual_tags]

    actual_tags = ['ORGANIZATION' if re.match('^.*ORG.*$', tag)
                       else tag for tag in actual_tags]

    actual_tags = ['O' if re.match('^.*MISC.*$', tag)
                       else tag for tag in actual_tags]
    return [sentences, all_tokens, actual_tags]
