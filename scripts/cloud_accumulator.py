import os
import json
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_available_models():
    """Fetches list of available models from Gemini API."""
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        res = requests.get(list_url)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            usable_models = [
                m["name"].replace("models/", "") 
                for m in models_data 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            print("Available models:", usable_models)
            return usable_models
    except Exception as e:
        print(f"Error listing models: {e}")
    return []

def fetch_and_synthesize():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return

    available = get_available_models()
    
    # Priority list of modern, active model candidates
    candidate_models = [
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-pro-latest",
        "gemini-2.5-flash-lite"
    ]

    # Filter candidates present in the user's available list
    targets = [m for m in candidate_models if m in available]
    if not targets:
        targets = available if available else ["gemini-flash-latest"]

    prompt = """
    You are an expert Pakistani Poultry Market Analyst.
    Perform a live web search for:
    1. Pakistani broiler rates, DOC chick prices, feed bag costs across Punjab, Sindh, KPK.
    2. Pak-Afghan border trade alerts (Torkham & Chaman closures, export duties).
    3. Global soybean/maize import prices and international trends affecting Pakistan poultry.

    Format the response cleanly in 4 Markdown sections:
    **📋 Executive Summary**
    **🔎 Key Insights & Analysis**
    **✅ Actionable Recommendations**
    **⚠️ Risk / Market Warning**
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}

    # Attempt execution with active model candidates
    for model_name in targets:
        print(f"Attempting generation with model: {model_name}")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        try:
            res = requests.post(url, headers=headers, json=payload)
            data = res.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                report = {
                    "status": "success",
                    "model_used": model_name,
                    "updated_at": "Hourly Live Analysis",
                    "content": text
                }
                with open("latest_news.json", "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                print(f"✅ Report successfully generated using {model_name}!")
                return
            else:
                print(f"Model {model_name} returned error: {json.dumps(data.get('error', data))}")
        except Exception as e:
            print(f"Request failed for {model_name}: {e}")

    print("❌ All model attempts failed.")

if __name__ == "__main__":
    fetch_and_synthesize()
