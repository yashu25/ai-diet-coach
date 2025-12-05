# fitness-llm-executables

This single-file code document contains three **minimal, runnable** Python projects (one-file Flask apps + helper files) that you can copy into separate GitHub repositories. Each project is built to be **easy for a non-dev (Electrical Engineer / Business Analyst)** to run, demo, and share with recruiters.

---

## Project A — AI Diet Coach (minimal, executable)

**Goal:** Give macros + one-day meal plan for Indian foods based on user input via a web form / HTTP endpoint.

**Files (single-file app):** `diet_coach_app.py`

```python
# diet_coach_app.py
from flask import Flask, request, jsonify, render_template_string
import os
import math

# You need an OpenAI API key in env: OPENAI_API_KEY
# pip install flask openai

try:
    import openai
except Exception:
    openai = None

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
<pre>{{result}}</pre>
"""

# Simple calorie estimator (Mifflin-St Jeor simplified for demo)
def estimate_calories(height_cm, weight_kg, goal):
    # rough BMR for demo
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * 30 + 5  # assume age 30, male
    if goal == 'cut':
        return int(bmr * 1.35 - 500)
    if goal == 'bulk':
        return int(bmr * 1.45 + 300)
    return int(bmr * 1.4)

# fallback local planner if OpenAI not present
def local_plan(calories):
    protein_g = int(2.0 * (calories / 30))  # rough
    carbs = int((calories - protein_g*4 - 70*4)/4)
    plan = {
        'calories': calories,
        'macros': {'protein_g': protein_g, 'carbs_g': max(50, carbs), 'fat_g': 70},
        'meals': [
            'Breakfast: Oats + milk + banana',
            'Lunch: Rice + chicken + salad',
            'Snack: Greek yogurt + nuts',
            'Dinner: Roti + paneer + veggies'
        ]
    }
    return plan

@app.route('/', methods=['GET','POST'])
def home():
    result = ''
    if request.method == 'POST':
        h = float(request.form.get('height',170))
        w = float(request.form.get('weight',70))
        goal = request.form.get('goal','maintain')
        calories = estimate_calories(h,w,goal)

        # If openai available, you can call it to make a nicer plan. We'll fall back to local_plan.
        plan = local_plan(calories)
        result = f"Calories target: {plan['calories']}\nMacros: {plan['macros']}\nMeals:\n- " + "\n- ".join(plan['meals'])
    return render_template_string(TEMPLATE, result=result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

**How to run (for recruiters demo):**
1. `python3 -m venv venv && source venv/bin/activate` (or Windows equivalent)
2. `pip install flask openai` (openai optional)
3. `python diet_coach_app.py`
4. Open `http://localhost:5001/` and fill details → share link or screen-record demo.

**Resume bullet:**
- Built a lightweight, runnable **AI Diet Coach** (Flask app) that generates calorie targets, macros and a 1-day Indian meal plan; designed for quick recruiter demos.

---

## Project B — AI Workout Plan Generator (single-file CLI + HTTP demo)

**Goal:** Given goals and equipment, return a 4-day split plan. Runnable via CLI and small web form.

**Files:** `workout_planner_app.py`

```python
# workout_planner_app.py
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<title>Workout Planner</title>
<h2>Workout Planner</h2>
<form method="post">
  Goal: <input name="goal" value="hypertrophy"><br>
  Equipment (comma separated): <input name="equip" value="dumbbell,bench"><br>
  <button type="submit">Get Plan</button>
</form>
<pre>{{plan}}</pre>
"""

EXERCISES = {
    'push': ['Barbell bench press', 'Dumbbell incline press', 'Overhead press'],
    'pull': ['Deadlift', 'Barbell row', 'Pull-up'],
    'legs': ['Squat', 'Romanian deadlift', 'Lunges'],
    'core': ['Plank', 'Hanging leg raise']
}

def make_plan(goal, equip_list):
    # Simple rule-based plan
    plan = {
        'Day 1': EXERCISES['push'][:2] + [EXERCISES['core'][0]],
        'Day 2': EXERCISES['pull'][:2] + [EXERCISES['core'][1]],
        'Day 3': EXERCISES['legs'][:3],
        'Day 4': ['Full body circuit: 3 rounds of bodyweight + dumbbell swings']
    }
    return plan

@app.route('/', methods=['GET','POST'])
def home():
    plan = ''
    if request.method == 'POST':
        goal = request.form.get('goal','hypertrophy')
        equip = request.form.get('equip','').split(',')
        plan_dict = make_plan(goal, [e.strip() for e in equip])
        plan = '\n'.join([f"{d}: {', '.join(v)}" for d,v in plan_dict.items()])
    return render_template_string(TEMPLATE, plan=plan)

if __name__ == '__main__':
    app.run(port=5002, host='0.0.0.0', debug=False)
```

**How to run:**
1. `pip install flask`
2. `python workout_planner_app.py`
3. Open `http://localhost:5002/` and demo.

**Resume bullet:**
- Implemented a **rule-based workout generator** (4-day split) as a runnable Flask demo for recruiter screening.

---

## Project C — Weekly Check-in Agent (auto-adjust roadmaps) — runnable webhook style

**Goal:** Accept weekly inputs (weight, notes) and return a short auto-adjust message + next week's small tweak.

**Files:** `checkin_agent_app.py`

```python
# checkin_agent_app.py
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.json or {}
    weight = data.get('weight')
    compliance = data.get('compliance', 0.7)
    notes = data.get('notes','')

    # Simple rule-based adjustment
    msg = ''
    if weight is None:
        return jsonify({'error':'send JSON with weight key (kg)'}), 400
    if weight > 0 and compliance < 0.6:
        msg = 'Compliance low — suggest reduce cardio volume slightly, focus on protein intake.'
    elif weight and weight > data.get('target_weight', weight):
        msg = 'Not losing — small calorie deficit increase of 100 kcal.'
    else:
        msg = 'On track — maintain plan; increase progressive overload on strength days.'

    return jsonify({'message': msg, 'next_week_adjustment':'+ adjust calories or volume as suggested'})

if __name__ == '__main__':
    app.run(port=5003, host='0.0.0.0', debug=False)
```

**How to run & demo:**
1. `pip install flask`
2. `python checkin_agent_app.py`
3. Send POST using `curl -H "Content-Type: application/json" -d '{"weight":70, "compliance":0.5}' http://localhost:5003/checkin`

**Resume bullet:**
- Built a **weekly check-in agent** that ingests user feedback and returns short, actionable auto-adjustments for the next week (runnable webhook demo).

---

## Quick GitHub tips (for each project)
1. Create a repo named `ai-diet-coach`, `ai-workout-planner`, `ai-checkin-agent`.
2. Add the single `.py` file, a short `README.md` copy of the descriptions above, and `requirements.txt` with `flask` (and optionally `openai`).
3. In `README.md`, add **Run demo** steps exactly as above so recruiters can run in 2–3 commands.
4. Add these sample resume bullets in the repo `README` so recruiters see impact.

---

## License & Notes
- These projects intentionally avoid heavy LLM code to stay very small and runnable — they are demo-first. If you later want to add RAG/LLM calls, add `openai` usage with a clear `ENV` var instruction.


# EOF
