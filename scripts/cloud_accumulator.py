import os
import json
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_available_model():
    """Dynamically fetches available models from Gemini API and picks the best match."""
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        res = requests.get(list_url)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            
            # Filter models that support content generation
            usable_models = [
                m["name"].replace("models/", "") 
                for m in models_data 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            print("Available models on your API key:", usable_models)
            
            # Priority order for preferred models
            preferred = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-2.5-flash"]
            for pref in preferred:
                if pref in usable_models:
                    return pref
            
            # Fallback to any usable model found
            if usable_models:
                return usable_models[0]
    except Exception as e:
        print(f"Error fetching model list: {e}")
        
    # Hardcoded fallback
    return "gemini-1.5-flash"

def fetch_and_synthesize():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return

    model_name = get_available_model()
    print(f"Selected Model: {model_name}")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    
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

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        
        if 'candidates' in data and len(data)['candidates'] > 0:
            text = data['candidates'][0]['content']['parts'][0]['text']
            report = {
                "status": "success",
                "model_used": model_name,
                "updated_at": "Hourly Live Analysis",
                "content": text
            }
            with open("latest_news.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print("✅ Report updated successfully!")
        else:
            print("API Error Response:", json.dumps(data, indent=2))
            
    except Exception as e:
        print(f"Error fetching report: {e}")

if __name__ == "__main__":
    fetch_and_synthesize()
