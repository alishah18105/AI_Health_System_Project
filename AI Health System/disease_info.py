from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import json

app = Flask(__name__)

# -------------------
# Load dataset CSV for training model
# -------------------
dataset_path = 'data/health_disease_dataset.csv'
data = pd.read_csv(dataset_path)

# Load disease info JSON
with open('data/health_dataset.json', 'r', encoding='utf-8') as f:
    diseases_list = json.load(f)

# Convert list of disease info to dict keyed by disease name
disease_info = {}
for d in diseases_list:
    disease_info[d['disease'].lower()] = {
        "description": d.get("description", "Description not available."),
        "medication": ", ".join(d.get("medication", [])),
        "prevention": ", ".join(d.get("prevention", [])),
        "diet_plan": ", ".join(d.get("diet_plan", []))
    }

# -------------------
# Train model on startup
# -------------------
def train_model():
    data['symptom'] = data['symptom'].str.lower()
    vectorizer = TfidfVectorizer(ngram_range=(1,3))  # capture multi-word symptoms
    X = vectorizer.fit_transform(data['symptom'])
    le = LabelEncoder()
    y = le.fit_transform(data['disease'])
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X, y)
    return model, vectorizer, le

model, vectorizer, le = train_model()

# -------------------
# Conversation state (simple in-memory)
# -------------------
conversation_state = {
    "last_diseases": [],
    "last_disease": None
}

# -------------------
# Predict top diseases (symptom-first flow)
# -------------------
@app.route('/predict', methods=['POST'])
def predict():
    data_in = request.json
    user_input = data_in.get('symptoms', '').lower().strip()
    if not user_input:
        return jsonify({"error": "Symptoms input is required."}), 400

    # 🔹 Step 1: Check if user directly mentioned a known disease
    for disease_name in disease_info.keys():
        if disease_name in user_input:
            conversation_state["last_disease"] = disease_name
            return jsonify({
                "direct_match": True,
                "disease": disease_name,
                "description": disease_info[disease_name].get("description", "Description not available."),
                "ask_more": f"What would you like to know about {disease_name}? (medication, prevention, diet plan)"
            })

    # 🔹 Step 2: Symptom-based prediction
    vect = vectorizer.transform([user_input])
    probs = model.predict_proba(vect)[0]

    disease_probs = {le.classes_[i]: probs[i] for i in range(len(probs))}

    # Count user symptoms
    input_symptoms = [s.strip() for s in user_input.split(",") if s.strip()]
    symptom_count = len(input_symptoms)

    # Filter based on min_symptoms_count and probability threshold
    valid_diseases = {}
    for disease, prob in disease_probs.items():
        required_count = data[data['disease'] == disease]['min_symptoms_count'].iloc[0]
        if symptom_count >= required_count and prob >= 0.02:
            valid_diseases[disease.lower()] = round(prob, 3)

    if not valid_diseases:
        return jsonify({"error": "Not enough symptoms provided to predict a disease."}), 400

    # Sort by probability and take top 5
    sorted_diseases = dict(sorted(valid_diseases.items(), key=lambda x: x[1], reverse=True)[:5])

    conversation_state["last_diseases"] = list(sorted_diseases.keys())
    conversation_state["last_disease"] = None  # reset until user chooses

    response = {
        "predictions": [{"disease": d, "probability": p} for d, p in sorted_diseases.items()],
        "ask_more": f"I found these possible diseases: {', '.join(sorted_diseases.keys())}. Which one do you want details about?"
    }
    return jsonify(response)

# -------------------
# Get disease info (step-by-step)
# -------------------
@app.route('/info', methods=['POST'])
def info():
    data_in = request.json
    disease_name = data_in.get('disease', '').lower()
    info_type = data_in.get('info_type', '').lower()

    # If disease not given, use last active disease
    if not disease_name and conversation_state["last_disease"]:
        disease_name = conversation_state["last_disease"]

    # If disease is still missing
    if not disease_name:
        return jsonify({"error": "Please specify a disease name."}), 400

    if disease_name not in disease_info:
        return jsonify({"error": f"No info available for {disease_name}."}), 404

    conversation_state["last_disease"] = disease_name

    if info_type not in ["description", "medication", "prevention", "diet plan"]:
        return jsonify({"error": "Invalid info type. Choose description, medication, prevention, or diet plan."}), 400

    info_text = disease_info[disease_name].get(info_type, "Information not available.")
    response = {
        "disease": disease_name,
        "info_type": info_type,
        "info": info_text,
        "ask_more": f"Do you want more info about {disease_name}, or switch to another disease?"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
