import csv, random
from collections import OrderedDict

N_ROWS = 500
OUTFILE = 'data/disease_dataset.csv'
SYMPTOMS = [
    'fever','cough','sore_throat','nasal_congestion','headache','body_pain','chills',
    'nausea','vomiting','diarrhea','abdominal_pain','burning_urination','frequent_urination',
    'fatigue','rash','joint_pain','bleeding_gums','retro_orbital_pain'
]

DISEASE_PROFILES = {
    'Common Cold': {'fever':0.6,'cough':0.8,'sore_throat':0.7,'nasal_congestion':0.8,'fatigue':0.3},
    'Malaria': {'fever':0.95,'headache':0.7,'body_pain':0.8,'chills':0.7,'nausea':0.3,'fatigue':0.6},
    'Typhoid': {'fever':0.9,'headache':0.6,'abdominal_pain':0.6,'diarrhea':0.3,'nausea':0.4,'fatigue':0.6},
    'Viral Fever': {'fever':0.9,'cough':0.5,'headache':0.7,'body_pain':0.6,'fatigue':0.7,'rash':0.15},
    'Urinary Tract Infection': {'burning_urination':0.9,'frequent_urination':0.85,'fever':0.2,'fatigue':0.2},
    'Dengue': {'fever':0.98,'headache':0.85,'body_pain':0.9,'rash':0.4,'joint_pain':0.7,'bleeding_gums':0.05,'retro_orbital_pain':0.6,'fatigue':0.7}
}

DISEASES = list(DISEASE_PROFILES.keys())

def sample_row(disease, row_id):
    profile = DISEASE_PROFILES[disease]
    row = OrderedDict()
    row['id'] = row_id
    row['age'] = random.randint(5,85)
    row['gender'] = random.choice(['M','F'])
    for s in SYMPTOMS:
        p = profile.get(s, 0.05)
        row[s] = 1 if random.random() < p else 0
    row['disease'] = disease
    return row

rows = [['id','age','gender'] + SYMPTOMS + ['disease']]
for i in range(1, N_ROWS+1):
    d = DISEASES[(i-1)%len(DISEASES)]
    rows.append(list(sample_row(d, i).values()))

with open(OUTFILE,'w',newline='') as f:
    csv.writer(f).writerows(rows)

print(f"Generated {N_ROWS} samples → {OUTFILE}")