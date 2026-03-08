from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import json
import uuid

app = FastAPI(title="AIvya Compliance API")

# Bedrock client
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-southeast-2"
)

class ScriptRequest(BaseModel):
    script: str


# -----------------------------
# Risk Level Function
# -----------------------------
def calculate_risk_level(score):

    if score <= 30:
        return "Low", "🟢"
    elif score <= 60:
        return "Medium", "🟡"
    else:
        return "High", "🔴"


# -----------------------------
# Risk Score Calculation
# -----------------------------
def compute_risk(detected):

    score = 0

    score += len(detected.get("brands", [])) * 20
    score += len(detected.get("characters", [])) * 30
    score += len(detected.get("music", [])) * 40
    score += len(detected.get("celebrities", [])) * 20

    if score > 100:
        score = 100

    return score


@app.get("/")
def home():
    return {"message": "AIvya Compliance API running 🚀"}


@app.post("/analyze")
def analyze_script(data: ScriptRequest):

    script = data.script

    prompt = f"""
You are an AI compliance engine.

Analyze the script and detect:
- brand names
- fictional characters
- music references
- celebrities

If any risks exist, generate issues and recommendations.

Return ONLY JSON in this format:

{{
 "detected": {{
   "brands": [],
   "characters": [],
   "music": [],
   "celebrities": []
 }},
 "issues": [],
 "recommendations": []
}}

Script:
{script}
"""

    try:

        body = json.dumps({
            "schemaVersion": "messages-v1",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 300,
                "temperature": 0.2
            }
        })

        response = bedrock.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())

        ai_text = result["output"]["message"]["content"][0]["text"]

        ai_json = json.loads(ai_text)

    except Exception as e:
        return {"error": str(e)}

    detected = ai_json.get("detected", {})

    # Compute risk score using Python
    score = compute_risk(detected)

    risk_level, indicator = calculate_risk_level(score)

    issues = ai_json.get("issues", [])
    recommendations = ai_json.get("recommendations", [])

    # Fallback safety
    if not issues:
        issues = ["Potential intellectual property usage detected"]

    if not recommendations:
        recommendations = [
            "Review content for copyright and trademark compliance",
            "Consider using royalty-free assets"
        ]

    return {
        "report_id": str(uuid.uuid4()),
        "risk_score": score,
        "risk_level": risk_level,
        "risk_indicator": indicator,
        "detected": detected,
        "issues": issues,
        "recommendations": recommendations
    }