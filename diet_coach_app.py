# diet_coach_app.py
# Improved demo: echoes inputs, shows explainable reasoning, per-meal macros and serving suggestions.
from flask import Flask, request, render_template_string
import os
import math

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>AI Diet Coach</title>
  <style>
    body{font-family: Arial, sans-serif; max-width:800px; margin:30px auto; padding:10px;}
    h1{color:#1a73e8;}
    form input[type=text]{width:120px; padding:6px; margin:6px 6px 6px 0;}
    .btn{background:#1a73e8;color:white;padding:8px 12px;border:none;border-radius:4px;cursor:pointer;}
    pre{background:#f5f5f5;padding:12px;border-radius:6px; white-space:pre-wrap;}
    .card{border:1px solid #eee;padding:12px;border-radius:6px;margin-top:12px;}
    .muted{color:#666;font-size:13px;}
  </style>
</head>
<body>
  <h1>AI Diet Coach — Demo (Explainable, Rule-based)</h1>
  <p class="muted">No external API used. This is a runnable, explainable nutrition demo for recruiter screening.</p>

  <form method="post">
    Height (cm): <input name="height" value="{{height}}"> 
    Weight (kg): <input name="weight" value="{{weight}}"> 
    Goal: <input name="goal" value="{{goal}}"> 
    <button class="btn" type="submit">Get Plan</button>
  </form>

  <div class="card">
    <strong>Inputs you submitted:</strong>
    <div class="muted">Height: {{height}} cm • Weight: {{weight}} kg • Goal: {{goal}}</div>
  </div>

  {% if explanation %}
    <div class="card">
      <strong>How the target was calculated (explainable):</strong>
      <pre>{{explanation}}</pre>
    </div>
  {% endif %}

  {% if result %}
    <div class="card">
      <strong>Daily target & macros:</strong>
      <pre>{{result}}</pre>
    </div>

    <div class="card">
      <strong>Per-meal split (approx):</strong>
      <pre>{{per_meal}}</pre>
    </div>

    <div class="card">
      <strong>Practical serving suggestions (approx):</strong>
      <pre>{{servings}}</pre>
    </div>

    <div class="card muted">
      <strong>Note:</strong> All food-portion numbers are approximate and for demo purposes. Protein/carbs/fat grams come from simple rules: protein = 2.0 g/kg bodyweight, fat = 25% calories, rest carbs.
    </div>
  {% endif %}
</body>
</html>
"""

def estimate_calories(height_cm, weight_kg, goal):
    # simple BMR formula (demo): Mifflin-St Jeor like (age assumed 30, male)
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * 30 + 5
    activity = 1.35
    if goal == 'cut':
        target = max(1200, int(bmr * activity - 400))
    elif goal == 'bulk':
        target = int(bmr * activity + 300)
    else:
        target = int(bmr * activity)
    return target, bmr, activity

def make_plan(calories, weight_kg):
    protein_g = int(round(2.0 * weight_kg))  # 2.0 g per kg
    fat_g = int(round((calories * 0.25) / 9))
    carbs_cal = calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = max(0, int(round(carbs_cal / 4)))

    # Per-meal split (4 meals): slightly more protein on main meals
    meals = 4
    prot_main = int(round(protein_g * 0.28))  # main meal 28%
    prot_other = int(round((protein_g - prot_main) / (meals - 1)))
    per_meal_protein = [prot_main] + [prot_other]*(meals-1)
    per_meal_carbs = [int(round(carbs_g / meals))]*meals
    per_meal_fat = [int(round(fat_g / meals))]*meals

    return {
        'calories': calories,
        'protein_g': protein_g,
        'carbs_g': carbs_g,
        'fat_g': fat_g,
        'per_meal': {
            'protein': per_meal_protein,
            'carbs': per_meal_carbs,
            'fat': per_meal_fat
        }
    }

def serving_suggestions(plan):
    # approximate nutrient densities (approx values)
    # chicken breast: 31g protein per 100g
    # paneer: 18g protein per 100g
    # egg: 6g protein per egg
    # cooked rice: 28g carbs per 100g
    # oats dry: 66g carbs per 100g (approx)
    # yogurt: 10g protein per 200g (approx)
    suggestions = []
    prot = plan['protein_g']
    carbs = plan['carbs_g']
    fat = plan['fat_g']

    # Example: translate protein to chicken grams if all from chicken
    chicken_needed_g = int(round((prot / 31.0) * 100))
    # But better mix: suggest per-meal examples
    per_meal_example = []
    for p in plan['per_meal']['protein']:
        # chicken portion for that meal:
        ch_g = int(round((p / 31.0) * 100))
        eggs = int(max(0, round(p / 6.0)))
        paneer_g = int(round((p / 18.0) * 100))
        per_meal_example.append({
            'protein_g': p,
            'chicken_g': ch_g,
            'eggs_equivalent': eggs,
            'paneer_g': paneer_g
        })

    # carbs per meal suggestions using rice
    per_meal_carbs = plan['per_meal']['carbs']
    per_meal_rice = [int(round(c/28.0*100)) for c in per_meal_carbs]  # cooked rice grams

    # Compose readable text
    suggestions.append(f"Total protein target: {prot} g/day (≈ {chicken_needed_g} g chicken breast if all from chicken).")
    suggestions.append("Better to mix sources: example per-meal protein options (approx):")
    for i, ex in enumerate(per_meal_example, start=1):
        suggestions.append(f" Meal {i}: ~{ex['protein_g']} g protein → ~{ex['chicken_g']} g chicken OR {ex['eggs_equivalent']} eggs OR ~{ex['paneer_g']} g paneer.")
    for i, r in enumerate(per_meal_rice, start=1):
        suggestions.append(f" Meal {i} carbs: ~{plan['per_meal']['carbs'][i-1]} g carbs → ~{r} g cooked rice.")
    suggestions.append(f"Total carbs: {carbs} g/day. Total fat: {fat} g/day.")
    return "\n".join(suggestions)

@app.route("/", methods=["GET", "POST"])
def home():
    # defaults shown in form
    height = request.form.get("height") if request.method == "POST" else "170"
    weight = request.form.get("weight") if request.method == "POST" else "70"
    goal = request.form.get("goal") if request.method == "POST" else "cut"

    explanation = ""
    result_text = ""
    per_meal_text = ""
    servings_text = ""

    try:
        h = float(height)
        w = float(weight)
        goal_lower = goal.strip().lower()
        calories, bmr, activity = estimate_calories(h, w, goal_lower)
        explanation = (f"BMR estimate (demo): {int(round(bmr))} kcal. "
                       f"Activity multiplier used: {activity}. "
                       f"Goal adjustment: {'-400 kcal' if goal_lower=='cut' else ('+300 kcal' if goal_lower=='bulk' else 'no adj')}. "
                       f"Resulting calorie target = {calories} kcal/day.")
        plan = make_plan(calories, w)
        result_text = (f"Calories: {plan['calories']} kcal/day\n"
                       f"Protein: {plan['protein_g']} g/day\n"
                       f"Carbs: {plan['carbs_g']} g/day\n"
                       f"Fat: {plan['fat_g']} g/day")
        # per-meal
        pm = plan['per_meal']
        per_meal_lines = []
        for i in range(len(pm['protein'])):
            per_meal_lines.append(f"Meal {i+1}: Protein {pm['protein'][i]} g | Carbs {pm['carbs'][i]} g | Fat {pm['fat'][i]} g")
        per_meal_text = "\n".join(per_meal_lines)
        servings_text = serving_suggestions(plan)
    except Exception as e:
        explanation = ""
        result_text = f"Error calculating plan: {e}"

    return render_template_string(TEMPLATE,
                                  height=height, weight=weight, goal=goal,
                                  explanation=explanation,
                                  result=result_text,
                                  per_meal=per_meal_text,
                                  servings=servings_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
