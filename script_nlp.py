import csv
import spacy
from abbrev import abbreviations
nlp = spacy.load("en_core_web_lg")

LINES_CSV = 'lines.csv'
MVR_CSV = 'mvr.csv'
OUT_CSV = 'out.csv'
WORD_LEN = 5
INJURY_WORDS = ['injury', 'fatal', 'pi', 'homicide', 'death', 'inj']

dummy = {}
COS_THRESH = 0.865

lines_defs = []
mvr_defs = {}
with open(LINES_CSV, newline='') as lines_csvfile:
    lines_reader = csv.DictReader(lines_csvfile, delimiter='\t')
    for lines_row in lines_reader:
        lines_words = [
            ''.join(ch for ch in x if ch.isalnum())
            for x in lines_row['line_def'].split(' ')
        ]
        lines_def = nlp(' '.join(lines_words))
        lines_defs.append(lines_def)

with open(MVR_CSV, newline='') as mvr_csvfile:
    mvr_reader = csv.DictReader(mvr_csvfile, delimiter='\t')
    for mvr_row in mvr_reader:
        mvr_tokens = list(nlp(mvr_row['desc']))
        mvr_desc_abbreviations_removed = ' '.join([abbreviations.get(str(e), str(e)) for e in mvr_tokens])
        mvr_def = nlp(mvr_desc_abbreviations_removed)
        mvr_defs[mvr_row['svc_code']] = mvr_def

with open(OUT_CSV, 'w', newline='') as out_csvfile:
    fieldnames = ['svc_code', 'description', 'augusta_risk_type', 'bodily_injury', 'cosine_similarities']
    writer = csv.DictWriter(out_csvfile, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()

    with open(MVR_CSV, newline='') as mvr_csvfile:
        mvr_reader = csv.DictReader(mvr_csvfile, delimiter='\t')
        for mvr_row in mvr_reader:
            matching_indexes = []
            cosine_similarities = []
            injury_flag = False
            for i, lines_def in enumerate(lines_defs, start=1):

                injury_flag = any([word in mvr_row['desc'] for word in INJURY_WORDS])

                mvr_def = mvr_defs[mvr_row['svc_code']]
                similarity = lines_def.similarity(mvr_def) if lines_def else 0

                if similarity >= COS_THRESH:
                    matching_indexes.append(str(i))
                    cosine_similarities.append(str(similarity))

            if not matching_indexes:
                matching_indexes.append('indeterminate')
            writer.writerow({
                'svc_code': mvr_row['svc_code'],
                'description': mvr_row['desc'].upper(),
                'augusta_risk_type': ', '.join(matching_indexes),
                'bodily_injury': injury_flag,
                'cosine_similarities': ', '.join(cosine_similarities)
            })
