import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

df = pd.read_csv('hearing_risk_data.csv') #datos pal modelo

# Encode risk level
df['risk_level'] = LabelEncoder().fit_transform(df['risk_level'])

X = df.drop('risk_level', axis=1)
y = df['risk_level']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))
joblib.dump(model, 'hearing_risk_model.pkl') #pa hacer el modelo