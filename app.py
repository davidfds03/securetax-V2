from flask import Flask, render_template, request
import joblib
import pandas as pd

# Load trained ML model
model = joblib.load("tax_model.joblib")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    estimated_tax = None
    agi = None
    effective_rate = None
    if request.method == "POST":
        filing_status = request.form["filing_status"]
        income_type = request.form["income_type"]
        income = float(request.form["income"])
        deductions = float(request.form["deductions"])

        if income_type == "monthly":
            income *= 12

        agi = max(income - deductions, 0)

        # Create input DataFrame for model
        input_data = pd.DataFrame([{
            "income": income,
            "deductions": deductions,
            "filing_status": filing_status
        }])

        estimated_tax = round(float(model.predict(input_data)[0]), 2)
        effective_rate = round((estimated_tax / income) * 100, 2) if income > 0 else 0

    return render_template("index.html", 
                           estimated_tax=estimated_tax, 
                           agi=agi, 
                           effective_rate=effective_rate)

if __name__ == "__main__":
    app.run(debug=True)
