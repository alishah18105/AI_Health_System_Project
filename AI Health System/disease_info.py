from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import json

app = Flask(__name__)

# Load dataset CSV for training model
dataset_path = 'data/health_dataset_training.csv'
data = pd.read_csv(dataset_path)

# Load and process disease info JSON
with open('data/health_dataset.json', 'r', encoding='utf-8') as f:
    diseases_list = json.load(f)

# Convert list of disease info to dict keyed by disease name,
# joining list fields into comma-separated strings for response
disease_info = {}
for d in diseases_list:
    disease_info[d['disease']] = {
        "description": d.get("description", "Description not available."),
        "medication": ", ".join(d.get("medication", [])),
        "prevention": ", ".join(d.get("prevention", [])),
        "diet_plan": ", ".join(d.get("diet_plan", []))
    }

# Train model on startup
def train_model():
    data['symptoms'] = data['symptoms'].str.lower()
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data['symptoms'])
    le = LabelEncoder()
    y = le.fit_transform(data['disease'])
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model, vectorizer, le

model, vectorizer, le = train_model()

@app.route('/predict', methods=['POST'])
def predict():
    data_in = request.json
    symptoms_text = data_in.get('symptoms', '').lower()
    if not symptoms_text:
        return jsonify({"error": "Symptoms input is required."}), 400

    vect = vectorizer.transform([symptoms_text])
    pred_index = model.predict(vect)[0]
    disease_name = le.classes_[pred_index]

    response = {
        "disease": disease_name,
        "description": disease_info.get(disease_name, {}).get("description", "Description not available."),
        "ask_more": "Do you want information about medication, prevention, or diet plan? Please reply with one of these options."
    }
    return jsonify(response)

@app.route('/info', methods=['POST'])
def info():
    data_in = request.json
    disease_name = data_in.get('disease', '')
    info_type = data_in.get('info_type', '').lower()  # medication, prevention, diet plan

    if disease_name not in disease_info:
        return jsonify({"error": "Disease information not found."}), 404

    if info_type not in ["medication", "prevention", "diet plan"]:
        return jsonify({"error": "Invalid info type. Choose medication, prevention, or diet plan."}), 400

    info_text = disease_info[disease_name].get(info_type, "Information not available.")
    response = {
        "disease": disease_name,
        "info_type": info_type,
        "info": info_text,
        "ask_more": "Do you want more information? Reply yes or no."
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
