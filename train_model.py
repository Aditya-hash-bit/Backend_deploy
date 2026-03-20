import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
data = pd.read_csv("../dataset/student_data.csv")

# Convert result to numeric
data["result"] = data["result"].map({"Pass": 1, "Fail": 0})

# Features
X = data[[
    "attendance",
    "study_hours",
    "marks",
    "assignment_score",
    "gpa"
]]

# Target
y = data["result"]

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)

# Save model
joblib.dump(model, "ml_model.pkl")

print("Model saved successfully")