# AI Diet Coach

Runnable Flask demo that produces calorie target, macros and a 1-day Indian meal plan.

## Run locally

1. Create venv:
   - Linux/Mac: `python3 -m venv venv && source venv/bin/activate`
   - Windows: `python -m venv venv` then `venv\Scripts\activate`

2. Install:
   `pip install -r requirements.txt`

3. Run:
   `python diet_coach_app.py`

4. Open:
   `http://localhost:5001/`

## Deploy (Render)
1. Connect this repo to Render.com (free tier).
2. Build command: `pip install -r requirements.txt`
3. Start command: `python diet_coach_app.py`
