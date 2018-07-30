import os
from nltk.parse import stanford

os.environ['STANFORD_PARSER'] = '/home/berfu/İndirilenler/stanford-parser-full-2018-02-27/jars'
os.environ['STANFORD_MODELS'] = '/home/berfu/İndirilenler/stanford-parser-full-2018-02-27/jars'

parser = stanford.StanfordParser(model_path="/home/berfu/İndirilenler/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models/edu/stanford/nlp/models/lexparser/englishRNN.ser.gz")
sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?"))
print(sentences)

# GUI
for line in sentences:
    for sentence in line:
        sentence.draw()

