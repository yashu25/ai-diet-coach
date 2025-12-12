import os
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # Add in Render

TEMPLATE = """
<!doctype html>
<title>AI Fitness Coach</title>
<h1>AI Fitness Coach (LLM Powered)</h1>

<form method="post">
  Height (cm): <input name="height" value="{{height}}"><br>
  Weight (kg): <input name="weight" value="{{weight}}"><br>
  Age: <input name="age" value="{{age}}"><br>
  Goal (cut/bulk/recomp): <input name="goal" value="{{goal}}"><br>
  Activity Level (sedentary/light/moderate/high/athlete): 
  <input name="activity" value="{{activity}}"><br>
  <button type="submit">Generate AI Plan</button>
</form>

{% if response %}
<h2>Your AI-Generated Fitness Plan:</h2>
<pre>{{response}}</pre>
{% endif %}
"""

def call_groq_llm(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a professional fitness and nutrition AI coach."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    r = requests.post(url, json=data, headers=headers)
    return r.json()["choices"][0]["message"]["content"]

@app.route("/", methods=["GET", "POST"])
def home():
    height = request.form.get("height", "170")
    weight = request.form.get("weight", "70")
    age = request.form.get("age", "28")
    goal = request.form.get("goal", "cut")
    activity = request.form.get("activity", "light")

    response = None

    if request.method == "POST":
        prompt = f"""
User stats:
Height: {height} cm
Weight: {weight} kg
Age: {age}
Goal: {goal}
Activity Level: {activity}

Give me:
1) My calorie target
2) Macro breakdown (protein, carbs, fat)
3) Activity multiplier you used
4) 1 sample full-day Indian meal plan with exact quantities (grams)
5) 1 sample gym workout plan (compound-focused)
6) Explanation of why you chose this plan

Return clean text. Do NOT hallucinate foods that don’t exist in India.
"""
        response = call_groq_llm(prompt)

    return render_template_string(TEMPLATE,
                                  response=response,
                                  height=height, weight=weight, age=age, goal=goal, activity=activity)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
