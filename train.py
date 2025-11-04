import pandas as pd, joblib, json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

csv_path = 'data/disease_dataset.csv'
df = pd.read_csv(csv_path)
df['gender_male'] = (df['gender']=='M').astype(int)
features = ['age','gender_male'] + [c for c in df.columns if c not in ('id','age','gender','disease')]
X, y = df[features], df['disease']
le = LabelEncoder(); y_enc = le.fit_transform(y)
X_train,X_test,y_train,y_test = train_test_split(X,y_enc,test_size=0.2,random_state=42)

model = RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42)
model.fit(X_train,y_train)

print('Accuracy:', accuracy_score(y_test, model.predict(X_test)))
print(classification_report(y_test, model.predict(X_test), target_names=le.classes_))

joblib.dump(model,'model/model.pkl')
json.dump(features, open('model/cols.json','w'))
json.dump({'classes': list(le.classes_)}, open('model/label_map.json','w'))