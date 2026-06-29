"""
AutoML Agent — trains multiple models, picks the best, explains with SHAP.
"""
import numpy as np
import pandas as pd
from typing import Optional
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, accuracy_score, classification_report
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier

# In-memory model store: {user_id: {model, feature_cols, target, task, score}}
_models: dict[str, dict] = {}

REGRESSION_MODELS = {
    "LinearRegression":    LinearRegression(),
    "Ridge":               Ridge(alpha=1.0),
    "RandomForest":        RandomForestRegressor(n_estimators=100, random_state=42),
    "GradientBoosting":    GradientBoostingRegressor(n_estimators=100, random_state=42),
    "DecisionTree":        DecisionTreeRegressor(max_depth=6, random_state=42),
}

CLASSIFICATION_MODELS = {
    "LogisticRegression":  LogisticRegression(max_iter=500, random_state=42),
    "RandomForest":        RandomForestClassifier(n_estimators=100, random_state=42),
    "GradientBoosting":    GradientBoostingClassifier(n_estimators=100, random_state=42),
    "DecisionTree":        DecisionTreeClassifier(max_depth=6, random_state=42),
}


def _detect_task(y: pd.Series) -> str:
    """Detect regression vs classification."""
    if y.dtype == object or y.nunique() <= 10:
        return "classification"
    return "regression"


def _prepare(df: pd.DataFrame, target: str):
    """Encode categoricals, drop nulls, split features/target."""
    df = df.dropna(subset=[target]).copy()
    X = df.drop(columns=[target])
    y = df[target]

    # Encode categorical features
    for col in X.select_dtypes("object").columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

    # Encode target if classification
    le_target = None
    if y.dtype == object:
        le_target = LabelEncoder()
        y = pd.Series(le_target.fit_transform(y.astype(str)), name=target)

    X = X.fillna(X.mean(numeric_only=True))
    return X, y, le_target


def run_automl(df: pd.DataFrame, target: str, user_id: str = "") -> dict:
    """Train multiple models, return best one with metrics."""
    if target not in df.columns:
        return {"error": f"Column '{target}' not found"}

    X, y, le_target = _prepare(df, target)
    task = _detect_task(y)
    models = CLASSIFICATION_MODELS if task == "classification" else REGRESSION_MODELS

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    results = []
    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            if task == "regression":
                score = round(r2_score(y_test, preds), 4)
                metric = "R²"
            else:
                score = round(accuracy_score(y_test, preds), 4)
                metric = "Accuracy"
            results.append({"name": name, "score": score, "model": model})
        except Exception as e:
            results.append({"name": name, "score": -999, "model": None, "error": str(e)})

    # Pick best
    best = max(results, key=lambda r: r["score"])

    # Store in memory
    if user_id and best["model"] is not None:
        _models[user_id] = {
            "model":        best["model"],
            "feature_cols": list(X.columns),
            "target":       target,
            "task":         task,
            "score":        best["score"],
            "metric":       metric,
        }

    leaderboard = [
        {"model": r["name"], metric: r["score"]}
        for r in sorted(results, key=lambda r: r["score"], reverse=True)
        if r["score"] != -999
    ]

    return {
        "best_model":  best["name"],
        "task":        task,
        "target":      target,
        "metric":      metric,
        "score":       best["score"],
        "leaderboard": leaderboard,
        "features":    list(X.columns),
        "train_rows":  len(X_train),
        "test_rows":   len(X_test),
    }


def predict(user_id: str, input_data: dict) -> dict:
    """Run prediction using the stored model for this user."""
    if user_id not in _models:
        return {"error": "No trained model found. Run AutoML first."}

    stored = _models[user_id]
    model = stored["model"]
    feature_cols = stored["feature_cols"]

    try:
        row = pd.DataFrame([input_data])
        # Align columns
        for col in feature_cols:
            if col not in row.columns:
                row[col] = 0
        row = row[feature_cols].fillna(0)

        pred = model.predict(row)
        return {
            "prediction": float(pred[0]) if stored["task"] == "regression" else int(pred[0]),
            "target": stored["target"],
            "task": stored["task"],
        }
    except Exception as e:
        return {"error": str(e)}


def explain_model(user_id: str, df: pd.DataFrame) -> dict:
    """Generate SHAP feature importance for the stored model."""
    if user_id not in _models:
        return {"error": "No trained model found. Run AutoML first."}

    stored = _models[user_id]
    model = stored["model"]
    feature_cols = stored["feature_cols"]

    try:
        import shap, json

        X, _, _ = _prepare(df, stored["target"])
        X = X[feature_cols].head(100)  # cap for speed

        # Use TreeExplainer for tree models, LinearExplainer for linear
        model_name = type(model).__name__
        if "Forest" in model_name or "Boosting" in model_name or "Tree" in model_name:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
        else:
            explainer = shap.LinearExplainer(model, X)
            shap_values = explainer.shap_values(X)

        # Mean absolute SHAP per feature
        mean_shap = np.abs(shap_values).mean(axis=0)
        importance = dict(zip(feature_cols, mean_shap.round(4).tolist()))
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

        # Build Plotly bar chart
        import plotly.express as px
        imp_df = pd.DataFrame(list(importance.items()), columns=["feature", "importance"])
        fig = px.bar(imp_df, x="importance", y="feature", orientation="h",
                     title="SHAP Feature Importance",
                     template="plotly_dark",
                     color="importance",
                     color_continuous_scale="Viridis")
        fig.update_layout(yaxis={"categoryorder": "total ascending"},
                          height=max(300, len(feature_cols) * 30))

        return {
            "importance": importance,
            "plotly_json": json.loads(fig.to_json()),
            "model": model_name,
            "target": stored["target"],
        }
    except Exception as e:
        # Fallback: use built-in feature_importances_ if available
        try:
            if hasattr(model, "feature_importances_"):
                imp = dict(zip(feature_cols, model.feature_importances_.round(4).tolist()))
                imp = dict(sorted(imp.items(), key=lambda x: x[1], reverse=True))
                import plotly.express as px, json
                imp_df = pd.DataFrame(list(imp.items()), columns=["feature", "importance"])
                fig = px.bar(imp_df, x="importance", y="feature", orientation="h",
                             title="Feature Importance (built-in)",
                             template="plotly_dark")
                return {"importance": imp, "plotly_json": json.loads(fig.to_json()),
                        "model": type(model).__name__, "target": stored["target"]}
        except Exception:
            pass
        return {"error": str(e)}
