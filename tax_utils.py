import re
import pandas as pd

def clean_income(value):
    return int(re.sub(r"[^\d]", "", str(value)))

def build_tax_model(csv_path):
    df = pd.read_csv(csv_path)

    df["AGI After deficits"] = df["AGI After deficits"].apply(clean_income)
    df["Bracket Tax %"] = df["Bracket Tax %"].astype(float)
    df["Type of filing"] = df["Type of filing"].str.lower().str.strip()

    bracket_dict = {}

    for filing_status in df["Type of filing"].unique():
        status_df = df[df["Type of filing"] == filing_status].sort_values(by="AGI After deficits")
        thresholds = status_df["AGI After deficits"].tolist()
        rates = status_df["Bracket Tax %"].tolist()

        brackets = []
        for i in range(0, len(thresholds), 2):
            lower = thresholds[i]
            upper = thresholds[i + 1] if i + 1 < len(thresholds) else float("inf")
            rate = rates[i] / 100
            brackets.append((lower, upper, rate))

        bracket_dict[filing_status] = brackets

    return bracket_dict

def calculate_tax(income, filing_status, brackets_by_status):
    status_key = {
        "single": "single filers/married filing separate (mfs)",
        "married": "married"
    }.get(filing_status.lower())

    if status_key not in brackets_by_status:
        raise ValueError("Unsupported filing status. Use 'single' or 'married'.")

    brackets = brackets_by_status[status_key]
    tax = 0.0
    for lower, upper, rate in brackets:
        if income > lower:
            taxable = min(income, upper) - lower
            tax += taxable * rate
        else:
            break
    return round(tax, 2)
