from flask import Flask, render_template, request
from tax_utils import calculate_tax, build_tax_model

# Build tax model from CSV
brackets_by_status = build_tax_model("tax_brackets.csv")

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
        estimated_tax = calculate_tax(agi, filing_status, brackets_by_status)
        effective_rate = round((estimated_tax / income) * 100, 2) if income > 0 else 0

    return render_template("index.html", 
                           estimated_tax=estimated_tax, 
                           agi=agi, 
                           effective_rate=effective_rate)

if __name__ == "__main__":
    app.run(debug=True)
