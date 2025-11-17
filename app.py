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
        "You are an expert code reviewer and security analyst. Examine the following code meticulously and identify "
        "any bugs, vulnerabilities, risky patterns, performance issues, or logic errors. Consider:\n\n"
        "- Memory leaks and resource management issues\n"
        "- Security vulnerabilities (SQL injection, XSS, etc.)\n"
        "- Race conditions and concurrency issues\n"
        "- Error handling gaps and unhandled exceptions\n"
        "- Type safety and null reference issues\n"
        "- Performance bottlenecks and inefficient algorithms\n"
        "- Code style and best practices violations\n"
        "- Off-by-one errors and boundary conditions\n"
        "- Unused variables or dead code\n"
        "- Logic errors and incorrect algorithms\n\n"
        "Respond in strict JSON format as a list of issues. Each issue must have:\n"
        "- \"line\": integer or null if unknown\n"
        "- \"severity\": one of [\"critical\", \"high\", \"medium\", \"low\"]\n"
        "- \"issue\": concise description of the problem\n"
        "- \"suggestion\": specific, actionable fix with code example if possible\n\n"
        "Code to review:\n"
        "```\n"
        f"{code_snippet}\n"
        "```\n\n"
        "Respond ONLY with valid JSON array, no additional text:"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1024
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