import joblib
import os
from scipy.sparse import hstack, csr_matrix
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Ensure these files are inside a "models" folder
TFIDF_PATH = "models/tfidf_vectorizer.pkl"
MODEL_PATH = "models/final_svm_fusion.pkl"
LE_PATH    = "models/label_encoder.pkl"
EMB_NAME_PATH = "models/embedding_model_name.txt"

print("Loading models...")

# 1. Load Scikit-Learn Artifacts
tfidf = joblib.load(TFIDF_PATH)
model = joblib.load(MODEL_PATH)
label_enc = joblib.load(LE_PATH)

# 2. Load Embedding Model Name from TXT file
if os.path.exists(EMB_NAME_PATH):
    with open(EMB_NAME_PATH, "r") as f:
        emb_model_name = f.read().strip()
else:
    # Fallback if file is missing
    print(f"Warning: {EMB_NAME_PATH} not found. Using default.")
    emb_model_name = "all-MiniLM-L6-v2"

print(f"Loading Sentence Transformer: {emb_model_name}...")
embedder = SentenceTransformer(emb_model_name)

print("✅ All models loaded successfully.")

def predict_text(text: str):
    """
    Returns: (label, score)
    - label: predicted class name (e.g., 'religion', 'age')
    - score: confidence probability (0.0 to 1.0)
    """
    # 1. Generate TF-IDF features
    x_tfidf = tfidf.transform([text])

    # 2. Generate Embedding features
    # convert_to_numpy=True is default; wrap in csr_matrix for stacking
    x_emb = embedder.encode([text], convert_to_numpy=True)
    
    # 3. FUSION (Stack them just like in training)
    # Result matches the shape [1, 3000 + 384]
    x_final = hstack([x_tfidf, csr_matrix(x_emb)])

    # 4. Predict
    pred_idx = model.predict(x_final)[0]
    
    # Decode label (Index -> String)
    label = label_enc.inverse_transform([pred_idx])[0]

    # Get Confidence Score
    score = 0.0
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(x_final)[0]
        score = float(max(proba))

    return str(label), score