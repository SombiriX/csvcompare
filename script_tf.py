from abbrev import abbreviations
from absl import logging
import csv
import numpy as np
import spacy
import tensorflow_hub as hub

nlp = spacy.load("en_core_web_lg")
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"  # @param ["https://tfhub.dev/google/universal-sentence-encoder/4", "https://tfhub.dev/google/universal-sentence-encoder-large/5"]
model = hub.load(module_url)
print("module %s loaded" % module_url)


def embed(input):
    return model(input)


LINES_CSV = 'lines.csv'
MVR_CSV = 'mvr.csv'
OUT_CSV = 'out.csv'
WORD_LEN = 5
INJURY_WORDS = {'injury', 'fatal', 'pi', 'homicide', 'death', 'inj'}
CORR_THRESH = 0.57

lines_defs = []
mvr_defs = []
with open(LINES_CSV, newline='') as lines_csvfile:
    lines_reader = csv.DictReader(lines_csvfile, delimiter='\t')
    for lines_row in lines_reader:
        lines_words = [
            ''.join(ch for ch in x if ch.isalnum())
            for x in lines_row['line_def'].split(' ')
        ]
        lines_defs.append(' '.join(lines_words))

with open(MVR_CSV, newline='') as mvr_csvfile:
    mvr_reader = csv.DictReader(mvr_csvfile, delimiter='\t')
    for mvr_row in mvr_reader:
        mvr_tokens = list(nlp(mvr_row['desc']))
        mvr_desc_abbreviations_removed = ' '.join([abbreviations.get(str(e), str(e)) for e in mvr_tokens])
        mvr_defs.append(mvr_desc_abbreviations_removed)

messages = lines_defs + mvr_defs

# Reduce logging output.
logging.set_verbosity(logging.ERROR)

message_embeddings = embed(messages)

# Correlation matrix
corr = np.inner(message_embeddings, message_embeddings)

mvr_range = range(len(lines_defs), len(lines_defs) + len(mvr_defs))
max_corr = CORR_THRESH

with open(OUT_CSV, 'w', newline='') as out_csvfile:
    fieldnames = ['svc_code', 'description', 'augusta_risk_type', 'bodily_injury', 'correlation']
    writer = csv.DictWriter(out_csvfile, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    with open(MVR_CSV, newline='') as mvr_csvfile:
        mvr_reader = csv.DictReader(mvr_csvfile, delimiter='\t')
        for i, mvr_row in enumerate(mvr_reader):
            matching_indexes = []
            correlation = []
            injury_flag = False
            for j in range(len(lines_defs)):
                mvr_idx = i + len(lines_defs)
                if corr[mvr_idx][j] >= CORR_THRESH:
                    matching_indexes.append(str(j + 1))
                    correlation.append(str(corr[mvr_idx][j]))
                    if corr[mvr_idx][j] > max_corr:
                        max_corr = corr[mvr_idx][j]
                        print("Max Correlation: {}".format(max_corr))
                        print("MVR: {}".format(mvr_row['desc']))
                        print("Line: {}".format(messages[j]))
                        print(' ')
            injury_flag = bool(set(messages[mvr_idx].split(' ')) & INJURY_WORDS)

            if not matching_indexes:
                matching_indexes.append('indeterminate')
            writer.writerow({
                'svc_code': mvr_row['svc_code'],
                'description': mvr_row['desc'].upper(),
                'augusta_risk_type': ', '.join(matching_indexes),
                'bodily_injury': injury_flag,
                'correlation': ', '.join(correlation)
            })
