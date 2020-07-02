import csv


LINES_CSV = 'lines.csv'
MVR_CSV = 'mvr.csv'
OUT_CSV = 'out.csv'
WORD_LEN = 4
INJURY_WORDS = ['injury', 'fatal', 'pi', 'homicide', 'death']

with open(OUT_CSV, 'w', newline='') as out_csvfile:
    fieldnames = ['svc_code', 'description', 'augusta_risk_type', 'bodily_injury']
    writer = csv.DictWriter(out_csvfile, fieldnames=fieldnames, delimiter='\t')

    writer.writeheader()

    with open(MVR_CSV, newline='') as mvr_csvfile:
        mvr_reader = csv.DictReader(mvr_csvfile, delimiter='\t')
        for mvr_row in mvr_reader:
            matching_indexes = []
            injury_flag = False
            with open(LINES_CSV, newline='') as lines_csvfile:
                lines_reader = csv.DictReader(lines_csvfile, delimiter='\t')
                for lines_row in lines_reader:
                    lines_words = [
                        ''.join(ch for ch in x if ch.isalnum())
                        for x in lines_row['line_def'].split(' ')
                        if len(x) > WORD_LEN
                    ]
                    if any([word in mvr_row['desc'] for word in lines_words]):
                        # Add line index to outputs for this row
                        matching_indexes.append(lines_row['index'])
                    injury_flag = any([word in mvr_row['desc'] for word in INJURY_WORDS])
            if not matching_indexes:
                matching_indexes.append('Unknown')
            writer.writerow({
                'svc_code': mvr_row['svc_code'],
                'description': mvr_row['desc'].upper(),
                'augusta_risk_type': ', '.join(matching_indexes),
                'bodily_injury': injury_flag
            })
