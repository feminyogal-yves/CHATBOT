from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from flask import Flask, request, jsonify, send_from_directory
import requests

# Initialize chatbot
chatbot = ChatBot("BakingBot")

# Train chatbot with basic responses
trainer = ListTrainer(chatbot)
trainer.train([
    "Hello", "Hi! I can help you with baking recipes. Just ask me for a cake, cookies, or any dessert!",
    "Can you give me a baking recipe?", "Sure! Just tell me which dessert you want! Just ask for a specific recipe!",
    "Goodbye", "Bye! Happy baking! 🍪"
])

# Function to fetch a SINGLE specific recipe from TheMealDB API
def get_recipe_by_name(dessert_name):
    if not dessert_name:
        return "Please tell me which dessert you'd like a recipe for!"

    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={dessert_name}"  # API endpoint for fetching recipes


    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()  # Parse the JSON response
        print("API Response:", data)  # Log the full API response


        if "meals" in data and data["meals"]:
            meal = data["meals"][0]  # Pick only the first exact match

            # Get ingredients & measurements
            ingredients = []
            for i in range(1, 21):
                ingredient = meal.get(f"strIngredient{i}")
                measure = meal.get(f"strMeasure{i}")
                if ingredient and ingredient.strip():
                    ingredients.append(f"- {measure} {ingredient}")

            # Build recipe message
            recipe_message = f"""
🍰 **{meal['strMeal']}**  
🔗 [Recipe Source]({meal.get('strSource', 'No link available')})  
📸 Image: {meal['strMealThumb']}

**Ingredients:**
{chr(10).join(ingredients)}

**Instructions:**
{meal['strInstructions']}
"""
            return recipe_message
        else:
            return f"Sorry, I couldn't find a recipe for **{dessert_name}**. Try a different name!"  # No meals found



    except requests.exceptions.RequestException as e:
        return f"Oops! There was an error fetching recipes: {e}"

# Initialize Flask app
app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip().lower()  # Get user input and normalize

    
    if "recipe" in user_input or "bake" in user_input or "specific" in user_input:  # Check if user wants a recipe

        dessert_name = user_input.replace("recipe", "").replace("bake", "").strip()
        if dessert_name:
            return jsonify({"response": get_recipe_by_name(dessert_name)})
        else:
            return jsonify({"response": "Please tell me which dessert you'd like a recipe for!"})
    
    else:
        response = chatbot.get_response(user_input)
        return jsonify({"response": str(response)})

@app.route('/', methods=['GET'])
def home():
    return send_from_directory('.', 'index.html')  # Serve the HTML file

if __name__ == '__main__':
    app.run(debug=True)
