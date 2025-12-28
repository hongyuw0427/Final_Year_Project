<<<<<<< Updated upstream
=======
#pip install -r requirements.txt
>>>>>>> Stashed changes
from flask import Flask, render_template, request, send_file, session, redirect, url_for, flash
from io import StringIO, BytesIO
import csv

from src.predict import predict_text
from src.db import init_db, insert_log, fetch_logs

app = Flask(__name__)
# 🔑 SECURITY: Secret key is required for sessions (Login) to work
app.secret_key = "fyp_secure_secret_key_2025"

with app.app_context():
    init_db()

# --- CONFIGURATION ---
THRESHOLD_LOW = 0.50
THRESHOLD_HIGH = 0.70

def get_status(score, label):
    """Returns (status_code, status_text)"""
    if label == "not_cyberbullying":
        return "safe", "✅ No Cyberbullying Detected"
    
    if score >= THRESHOLD_HIGH:
        return "danger", "🚫 Cyberbullying Detected"
    elif score >= THRESHOLD_LOW:
        return "warning", "⚠️ Potential Harassment Detected"
    else:
        return "safe", "✅ No Cyberbullying Detected"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        text = (request.form.get("text") or "").strip()
        if text:
            label, score = predict_text(text)
            status_code, status_text = get_status(score, label)
            
            if status_code == "safe":
                label = "not_cyberbullying"

            result = {
                "text": text,
                "label": label,
                "score": score,
                "status_code": status_code,
                "status_text": status_text
            }
            insert_log(text, label, score)

    return render_template("index.html", result=result)

# --- 🔐 NEW: LOGIN ROUTE ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # 🛡️ Hardcoded Credentials for FYP (Simple & Effective)
        # You can change these to whatever you want
        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            flash("❌ Invalid Username or Password", "error")
    
    return render_template("login.html")

# --- 🔓 NEW: LOGOUT ROUTE ---
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("✅ You have been successfully logged out.", "info")
    return redirect(url_for("index"))

# --- PROTECTED ADMIN ROUTE ---
@app.route("/admin")
def admin():
    # 🚫 Check if user is logged in
    if not session.get("admin_logged_in"):
        flash("⚠️ Access Denied. Please log in to view logs.", "warning")
        return redirect(url_for("login"))

    raw_logs = fetch_logs(limit=300)
    processed_logs = []
    
    for row in raw_logs:
        pred_label = row[3]
        score = row[4] if row[4] else 0.0
        status_code, status_text = get_status(score, pred_label)
        
        processed_logs.append({
            "id": row[0],
            "time": row[1],
            "text": row[2],
            "type": pred_label, 
            "score": score,
            "status_code": status_code,
            "status_text": status_text
        })

    return render_template("admin.html", logs=processed_logs)

@app.route("/admin/export_csv")
def export_csv():
    # 🚫 Protect Export too
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    logs = fetch_logs(limit=10000)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Time", "Text", "Prediction Type", "Score"])
    for row in logs:
        writer.writerow(row)

    mem = BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    output.close()

    return send_file(mem, as_attachment=True, download_name="logs.csv", mimetype="text/csv")

if __name__ == "__main__":
    app.run(debug=True)