# app.py
import os
import json
from fastapi import FastAPI, Body
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4.1"


def analyze_code_for_bugs(code_snippet: str) -> list:
    prompt = (
        "You are an expert code reviewer. Examine the following code and identify "
        "any bugs, risky patterns, or logic issues. Respond in strict JSON format "
        "as a list of issues, where each issue has:\n"
        "- line (integer)\n"
        "- issue (string)\n"
        "- suggestion (string)\n\n"
        "Code:\n"
        f"{code_snippet}\n\n"
        "JSON:"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=512
    )

    raw_output = response.choices[0].message.content
    if raw_output is None:
        raw_output = ""

    if "[" not in raw_output or "]" not in raw_output:
        return [{"line": None, "issue": "Parsing error", "suggestion": raw_output}]

    try:
        start = raw_output.index("[")
        end = raw_output.rindex("]") + 1
        issues = json.loads(raw_output[start:end])
    except Exception:
        issues = [{"line": None, "issue": "Parsing error", "suggestion": raw_output}]

    return issues


@app.post("/find-bugs")
def find_bugs(data: dict = Body(...)):
    code = data.get("code") or ""
    result = analyze_code_for_bugs(code)
    return {"issues": result}
