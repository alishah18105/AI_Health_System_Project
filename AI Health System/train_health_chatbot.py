import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils.multiclass import unique_labels


# Load data
data = pd.read_csv('health_dataset_training.csv')

# Preprocess symptoms text
data['symptoms'] = data['symptoms'].str.lower()

# Vectorize symptoms
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['symptoms'])

# Encode labels
le = LabelEncoder()
y = le.fit_transform(data['disease'])

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Get only the labels present in y_test and y_pred
labels = unique_labels(y_test, y_pred)

# Use these labels for classification report
print(classification_report(y_test, y_pred, labels=labels, target_names=le.classes_[labels]))
# Example prediction function
def predict_disease(symptoms_text):
    symptoms_text = symptoms_text.lower()
    vect = vectorizer.transform([symptoms_text])
    pred_index = model.predict(vect)[0]
    return le.classes_[pred_index]

# Test example
test_input = "fever, headache, nausea"
print(f"Predicted disease for symptoms '{test_input}': {predict_disease(test_input)}")
