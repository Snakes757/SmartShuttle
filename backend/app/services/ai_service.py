import os
import json
import google.generativeai as genai
from app.schemas import PickUpPointCreate, RouteBase

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "fallback_key")
if GEMINI_API_KEY != "fallback_key":
    genai.configure(api_key=GEMINI_API_KEY)

async def estimate_tolls_for_route(point_a: str, point_b: str) -> float:

    if GEMINI_API_KEY == "fallback_key":
        return 0.0 # Fallback if no API key is provided

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"You are a routing and toll estimation assistant for a South African shuttle service. "
            f"A trip is planned from '{point_a}' to '{point_b}'. "
            f"Estimate the total cost of standard passenger vehicle toll gates encountered on this specific route in ZAR (South African Rands). "
            f"Respond STRICTLY in JSON format with a single key 'estimated_tolls_zar' containing only the float value. Example: {{\"estimated_tolls_zar\": 150.50}}"
        )

        response = model.generate_content(prompt)

        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_response)
        return float(data.get("estimated_tolls_zar", 0.0))

    except Exception as e:
        print(f"AI Toll Estimation Error: {e}")
        return 0.0 # Fallback to 0.0 if the AI fails, ensuring the system doesn't crash

async def evaluate_detour_viability(pickup: PickUpPointCreate, route: RouteBase) -> dict:

    if GEMINI_API_KEY == "fallback_key":
        return {"status": "error", "message": "AI API Key is not configured in environment."}

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = (
            f"You are a routing assistant. A shuttle route goes from {route.point_a_start} "
            f"to {route.point_b_end}. A passenger requested a pick up at {pickup.location_name} "
            f"with a maximum allowable detour radius of {pickup.radius}. Based on typical geography, "
            f"does this pick-up point lie outside the radius and affect the route heavily?"
        )

        response = model.generate_content(prompt)

        return {
            "status": "success",
            "location_name": pickup.location_name,
            "ai_evaluation": response.text
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}