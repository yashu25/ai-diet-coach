from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# HTML Template
TEMPLATE = """
<!doctype html>
<title>AI Diet Coach</title>
<h2>AI Diet Coach — enter your details</h2>
<form method="post">
  Height (cm): <input name="height" value="170"><br>
  Weight (kg): <input name="weight" value="70"><br>
  Goal (cut/bulk/maintain): <input name="goal" value="cut"><br>
  <button type="submit">Get Plan</button>
</form>
<hr>
<pre>{{result}}</pre>
"""

# Calorie calculator
def estimate_calories(height_cm, weight_kg, goal):
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * 30 + 5  
    activity = 1.35  

    if goal == "cut":
        return max(1200, int(bmr * activity - 400))
    if goal == "bulk":
        return int(bmr * activity + 300)
    return int(bmr * activity)

# Generate diet plan
def generate_plan(cal, weight):
    protein = int(weight * 2)
    fat = int(cal * 0.25 / 9)
    carbs = int((cal - protein * 4 - fat * 9) / 4)

    meals = [
        "Breakfast: Oats + milk + banana",
        "Lunch: Rice/roti + chicken/paneer + salad",
        "Snack: Yogurt + fruits",
        "Dinner: Roti + vegetables + eggs/paneer"
    ]

    return f"""
Calories: {cal}
Protein: {protein}g
Carbs: {carbs}g
Fat: {fat}g

Meals:
- {meals[0]}
- {meals[1]}
- {meals[2]}
- {meals[3]}
"""

# ✅ THE ROUTE (THIS FIXES YOUR ISSUE)
@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    if request.method == "POST":
        try:
            h = float(request.form["height"])
            w = float(request.form["weight"])
            goal = request.form["goal"].lower()

            cal = estimate_calories(h, w, goal)
            result = generate_plan(cal, w)

        except Exception as e:
            result = f"Error: {e}"

    return render_template_string(TEMPLATE, result=result)

# Run for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
