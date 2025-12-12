# diet_coach_app.py
# Minimal, runnable Flask app — no OpenAI key required.
# Purpose: takes Height, Weight, Goal and returns calorie target + simple meal plan.

from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>AI Diet Coach (Minimal)</title>
<h2>AI Diet Coach — enter your details</h2>
<form method="post">
  Height cm: <input name="height" value="170"><br>
  Weight kg: <input name="weight" value="70"><br>
  Goal (cut/bulk/maintain): <input name="goal" value="cut"><br>
  <button type="submit">Get Plan</button>
</form>
<hr>
<pre>{{result}}</pre>
"""

def estimate_calories(height_cm, weight_kg, goal):
    # simplified BMR estimate (assume age 30, male) — demo only
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * 30 + 5
    activity = 1.35  # light activity for demo
    if goal == 'cut':
        return max(1200, int(bmr * activity - 500))
    if goal == 'bulk':
        return int(bmr * (1.45) + 300)
    return int(bmr * activity)

def local_plan(calories, weight_kg):
    # simple macro calc: protein 2.0 g/kg, fat 25% calories, rest carbs
    protein_g = int(2.0 * weight_kg)
    fat_cal = int(calories * 0.25)
    fat_g = int(fat_cal / 9)
    carbs_cal = calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = max(0, int(carbs_cal / 4))
    meals = [
        "Breakfast: Oats + milk + banana",
        "Lunch: Rice/roti + chicken or paneer + salad",
        "Snack: Yogurt + fruits or nuts",
        "Dinner: Roti + vegetable + protein (eggs/beans)"
    ]
    return {
        'calories': calories,
        'macros': {'protein_g': protein_g, 'carbs_g': carbs_g, 'fat_g': fat_g},
        'meals': meals
    }

@app.route('/', methods=['GET','POST'])
def home():
    result = ''
    if request.method == 'POST':
        try:
            h = float(request.form.get('height', 170))
            w = float(request.form.get('weight', 70))
            goal = request.form.get('goal', 'maintain').lower()
            calories = estimate_calories(h, w, goal)
            plan = local_plan(calories, w)
            result = f"Calories target: {plan['calories']} kcal\\nMacros: {plan['macros']}\\nMeals:\\n- " + "\\n- ".join(plan['meals'])
        except Exception as e:
            result = f"Error: {e}"
    return render_template_string(TEMPLATE, result=result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    # host=0.0.0.0 so Render/GH pages can reach it
    app.run(host='0.0.0.0', port=port, debug=False)
