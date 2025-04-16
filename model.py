import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

from tax_utils import calculate_tax, build_tax_model

# Load tax brackets
brackets_by_status = build_tax_model("tax_brackets.csv")

# Generate synthetic data
np.random.seed(42)
samples = 5000

data = {
    "income": np.random.uniform(10000, 250000, samples),
    "deductions": np.random.uniform(0, 15000, samples),
    "filing_status": np.random.choice(["single", "married"], samples)
}

df = pd.DataFrame(data)
df["adjusted_income"] = (df["income"] - df["deductions"]).clip(lower=0)
df["tax"] = df.apply(lambda row: calculate_tax(row["adjusted_income"], row["filing_status"], brackets_by_status), axis=1)

# ML input and target
X = df[["income", "deductions", "filing_status"]]
y = df["tax"]

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["filing_status"])
    ],
    remainder="passthrough"
)

model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print(f"RMSE: ${rmse:.2f}")

# Save the model
joblib.dump(model, "tax_model.joblib")
