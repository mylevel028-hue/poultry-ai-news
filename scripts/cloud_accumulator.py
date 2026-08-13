import os
import json
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def fetch_and_synthesize():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return

    # Endpoint using gemini-2.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}]
    }

    headers = {'Content-Type': 'application/json'}

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        
        if 'candidates' in data and len(data['candidates']) > 0:
            text = data['candidates'][0]['content']['parts'][0]['text']
            report = {
                "status": "success",
                "updated_at": "Hourly Live Analysis",
                "content": text
            }
            with open("latest_news.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print("Report updated successfully.")
        else:
            print("API Error Response:", json.dumps(data, indent=2))
            
    except Exception as e:
        print(f"Error fetching report: {e}")

if __name__ == "__main__":
    fetch_and_synthesize()
