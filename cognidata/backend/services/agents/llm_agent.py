"""
LLM Agent — GPT-level intelligence layer.

Features:
- Auto-detects best available model (gpt-4o → gpt-3.5-turbo)
- Conversation memory (last 10 exchanges)
- Safe pandas code execution with rich stdlib access
- Smart chart type selection
- Compact data summaries (low token usage)
"""
import os
import re
import numpy as np
import pandas as pd
from typing import Optional


# ── Model resolution ──────────────────────────────────────────────────────────

def _get_client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

def _best_model() -> str:
    try:
        from services.agents.model_resolver import resolve_model
        return resolve_model(os.environ.get("OPENAI_API_KEY", ""))
    except Exception:
        return "gpt-3.5-turbo"


# ── Data summary (token-efficient) ────────────────────────────────────────────

def _compact_summary(df: pd.DataFrame, max_rows: int = 5) -> str:
    nums = df.select_dtypes(include=np.number)
    cats = df.select_dtypes(include="object")
    lines = [
        f"Shape: {df.shape[0]} rows × {df.shape[1]} columns",
        f"Columns: {list(df.columns)}",
        f"Numeric: {nums.columns.tolist()}",
        f"Categorical: {cats.columns.tolist()}",
        f"Missing: {df.isnull().sum()[df.isnull().sum()>0].to_dict()}",
    ]
    if not nums.empty:
        desc = nums.describe().loc[["mean","std","min","max"]].round(2)
        lines.append(f"Stats:\n{desc.to_string()}")
    if not cats.empty:
        for col in cats.columns[:3]:
            lines.append(f"{col} samples: {df[col].value_counts().head(5).to_dict()}")
    lines.append(f"\nFirst {max_rows} rows:\n{df.head(max_rows).to_string()}")
    return "\n".join(lines)


# ── Safe code execution ───────────────────────────────────────────────────────

_SAFE_BUILTINS = {
    "len": len, "range": range, "list": list, "dict": dict,
    "str": str, "int": int, "float": float, "bool": bool,
    "round": round, "abs": abs, "sum": sum, "min": min, "max": max,
    "sorted": sorted, "enumerate": enumerate, "zip": zip,
    "print": print, "type": type, "isinstance": isinstance,
}

def _execute_code(code: str, df: pd.DataFrame):
    """Execute LLM-generated pandas code safely."""
    # Strip markdown fences
    code = re.sub(r"```(?:python)?|```", "", code).strip()

    local = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "__builtins__": _SAFE_BUILTINS,
    }
    exec(code, local)
    return local.get("result")


# ── Main query function ───────────────────────────────────────────────────────

def run_llm_query(question: str, df: Optional[pd.DataFrame],
                  user_id: str = "", history: list = None):
    """
    Generate and execute pandas code via LLM.
    Uses conversation history for context-aware responses.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None, "", "No OpenAI API key configured"

    try:
        client = _get_client()
        model  = _best_model()
        summary = _compact_summary(df) if df is not None else "No dataset loaded."

        system_msg = f"""You are an expert Python data analyst with access to a pandas DataFrame named 'df'.

Dataset summary:
{summary}

Rules:
- Write ONLY executable Python pandas/numpy code
- Store the final answer in a variable named 'result'
- result should be a DataFrame, Series, scalar, or list
- No explanations, no markdown fences, no print statements
- Use df.copy() if modifying the dataframe"""

        messages = [{"role": "system", "content": system_msg}]

        # Add conversation history for context
        if history:
            messages.extend(history[-6:])  # last 3 exchanges

        messages.append({"role": "user", "content": question})

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=600,
        )
        code = resp.choices[0].message.content.strip()

        if df is not None:
            result = _execute_code(code, df)
        else:
            result = None

        return result, code, "success"

    except Exception as e:
        return None, "", str(e)


# ── Insight generation ────────────────────────────────────────────────────────

def run_insight(df: Optional[pd.DataFrame], api_key: str,
                history: list = None) -> str:
    if df is None:
        return "No dataset loaded. Upload a file first."
    try:
        client = _get_client()
        model  = _best_model()
        summary = _compact_summary(df, max_rows=3)

        messages = [
            {"role": "system", "content":
             "You are a senior business analyst. Be specific, concise, and actionable. "
             "Always reference actual numbers from the data."},
        ]
        if history:
            messages.extend(history[-4:])

        messages.append({"role": "user", "content":
            f"Dataset:\n{summary}\n\n"
            "Provide exactly 5 actionable business insights as bullet points. "
            "For each: state the finding with specific numbers, explain why it matters, "
            "and give a concrete recommendation."})

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=600,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate insights: {e}"


# ── Smart chart type selection ────────────────────────────────────────────────

def select_chart_type(result_df: pd.DataFrame, question: str) -> str:
    """Ask LLM to pick the best chart type for the result."""
    try:
        client = _get_client()
        cols = list(result_df.columns) if hasattr(result_df, "columns") else []
        dtypes = {c: str(t) for c, t in result_df.dtypes.items()} if hasattr(result_df, "dtypes") else {}

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",  # fast model for this simple task
            messages=[{"role": "user", "content":
                f"Question: {question}\nResult columns: {cols}\nDtypes: {dtypes}\n\n"
                "Return ONLY one word: bar, line, scatter, pie, histogram, heatmap, or table"}],
            temperature=0,
            max_tokens=10,
        )
        return resp.choices[0].message.content.strip().lower()
    except Exception:
        return "table"
