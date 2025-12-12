# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import torch
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# ----- SET LOCAL MODEL PATH -----
# Make sure this folder exists next to main.py:
# emotion/
#     main.py
#     mental_health_emotion_model/
MODEL_PATH = "./mental_health_emotion_model"

# ----- Load model & tokenizer -----
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

# Put model on GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# ----- LABELS (must match training order) -----
label_cols: List[str] = [
    "admiration","amusement","anger","annoyance","approval","caring",
    "confusion","curiosity","desire","disappointment","disapproval",
    "disgust","embarrassment","excitement","fear","gratitude","grief",
    "joy","love","nervousness","optimism","pride","realization",
    "relief","remorse","sadness","surprise","neutral"
]

# ----- Emotion → Risk mapping -----
emotion_to_risk = {
    'admiration':'low','amusement':'low','anger':'high','annoyance':'moderate',
    'approval':'low','caring':'low','confusion':'moderate','curiosity':'low',
    'desire':'low','disappointment':'moderate','disapproval':'moderate',
    'disgust':'high','embarrassment':'moderate','excitement':'low','fear':'high',
    'gratitude':'low','grief':'high','joy':'low','love':'low','nervousness':'moderate',
    'optimism':'low','pride':'low','realization':'low','relief':'low','remorse':'high',
    'sadness':'high','surprise':'low','neutral':'low'
}

# ----- Prediction function -----
def predict_emotions(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    # Move tensors to model device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.sigmoid(logits).cpu().numpy()[0]

    # Pick emotions with probability > 0.5
    indices = np.where(probs > 0.5)[0]

    # If nothing passed threshold → choose top 1
    if len(indices) == 0:
        indices = [int(np.argmax(probs))]

    predicted_emotions = [label_cols[i] for i in indices]
    predicted_scores = [float(probs[i]) for i in indices]

    return list(zip(predicted_emotions, predicted_scores))


# ----- Risk mapping -----
def map_risk(preds):
    risks = [emotion_to_risk.get(e, "low") for e, _ in preds]
    if "high" in risks:
        return "high"
    elif "moderate" in risks:
        return "moderate"
    return "low"


# ----- FastAPI Models -----
class TextInput(BaseModel):
    text: str

class EmotionScore(BaseModel):
    emotion: str
    score: float

class PredictionResponse(BaseModel):
    risk: str
    predictions: List[EmotionScore]


# ----- FastAPI App -----
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Emotion Model API is running ✔"}


@app.post("/predict", response_model=PredictionResponse)
def predict(input_data: TextInput):
    preds = predict_emotions(input_data.text)
    risk = map_risk(preds)
    return {
        "risk": risk,
        "predictions": [
            {"emotion": emo, "score": score} for emo, score in preds
        ]
    }
