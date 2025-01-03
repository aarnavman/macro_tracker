import streamlit as st
import requests
import pandas as pd

def add_custom_css():
    st.markdown("""
        <style>
        /* CSS Variables for Consistent Theming */
        :root {
            --primary-color: #1ABC9C;
            --secondary-color: #34495E;
            --accent-color: #E74C3C;
            --text-color: #fefefe;
            --shadow-color: rgba(0, 0, 0, 0.25);
            --hover-color: #16a085;
        }

        /* Gradient Background */
        body {
            background: linear-gradient(90deg, #1d2671, #c33764);
            background-size: 400% 400%;
            animation: gradientAnimation 10s ease infinite;
            font-family: 'Poppins', sans-serif;
            color: var(--text-color);
            margin: 0;
            padding: 0;
        }

        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* General Page Styling */
        .main {
            padding: 30px;
            line-height: 1.8;
            transition: all 0.3s ease-in-out;
        }

        /* Headings Styling */
        h1, h2, h3 {
            text-align: center;
            font-weight: 1000;
            margin-bottom: 20px;
            text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.4);
        }

        h1 {
            font-size: 4em;
            color: var(--primary-color);
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        h2 {
            font-size: 2.5em;
            color: var(--accent-color);
        }

        /* Card Container Styling */
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 30px;
            padding: 20px 0;
        }

        /* Card Styling */
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            box-shadow: 0 8px 24px var(--shadow-color);
            padding: 30px;
            width: 350px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.4s ease, box-shadow 0.4s ease;
        }

        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
        }

        .card h3 {
            font-size: 2em;
            margin-bottom: 15px;
            color: var(--hover-color);
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
        }

        .card p {
            font-size: 1.2em;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.8;
        }

        /* Buttons Styling */
        .stButton button, .card-button {
            background-color: var(--primary-color);
            color: white;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 8px;
            padding: 15px 30px;
            border: none;
            box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: transform 0.3s ease, background-color 0.3s ease;
        }

        .stButton button:hover, .card-button:hover {
            background-color: var(--hover-color);
            transform: scale(1.05);
            box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.3);
        }

        .stButton button:active, .card-button:active {
            background-color: var(--secondary-color);
            transform: scale(0.96);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .card-container {
                flex-direction: column;
                align-items: center;
            }

            .card {
                width: 90%;
            }
        }
        </style>
    """, unsafe_allow_html=True)


API_KEY = "c5tmsb8zUFSdHNtB4dGVeeEUyHveyggVlVdia5he"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# Function to search for foods
def search_food(query):
    url = f"{BASE_URL}/foods/search"
    params = {
        "query": query,
        "api_key": API_KEY,
        "pageSize": 10  # Limit results to 10
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Function to get food details
def get_food_details(fdc_id):
    url = f"{BASE_URL}/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Streamlit App
st.title("Macro Tracker")

# User Macro Goals
st.sidebar.header("Set Macro Goals")
carb_goal = st.sidebar.number_input("Carbs Goal (g)", value=150)
protein_goal = st.sidebar.number_input("Protein Goal (g)", value=100)
fat_goal = st.sidebar.number_input("Fat Goal (g)", value=50)

# Store meals data
if "meals" not in st.session_state:
    st.session_state.meals = {"Breakfast": [], "Lunch": [], "Dinner": []}

# Meal Category
meal_category = st.selectbox("Select Meal Category", ["Breakfast", "Lunch", "Dinner"])

# Food Search
st.header(f"Search for Foods - {meal_category}")
food_query = st.text_input("Enter a food name", placeholder="e.g., chicken breast, rice")
if st.button("Search"):
    if food_query:
        search_results = search_food(food_query)
        if search_results and "foods" in search_results:
            food_items = search_results["foods"]
            food_options = {food["description"]: food["fdcId"] for food in food_items}
            selected_food_name = st.selectbox("Select a food", list(food_options.keys()))
            selected_fdc_id = food_options[selected_food_name]

            # Fetch and display food details
            food_details = get_food_details(selected_fdc_id)
            if food_details:
                nutrients = food_details.get("foodNutrients", [])
                # Extracting the nutrient data for carbs, protein, fat
                carb_amount = 0
                protein_amount = 0
                fat_amount = 0
                for nutrient in nutrients:
                    nutrient_name = nutrient.get("nutrient", {}).get("name", "").lower()
                    if "carbohydrate" in nutrient_name:
                        carb_amount = nutrient.get("amount", 0)
                    elif "protein" in nutrient_name:
                        protein_amount = nutrient.get("amount", 0)
                    elif "fat" in nutrient_name:
                        fat_amount = nutrient.get("amount", 0)

                # Storing the nutrient values for the selected food
                st.session_state.meals[meal_category].append({
                    "food_name": selected_food_name,
                    "carbs": carb_amount,
                    "protein": protein_amount,
                    "fat": fat_amount
                })

                # Displaying the nutrient data
                nutrient_data = {
                    "Nutrient": ["Carbohydrates", "Protein", "Fat"],
                    "Amount (g)": [carb_amount, protein_amount, fat_amount],
                }
                nutrient_df = pd.DataFrame(nutrient_data)
                st.subheader(f"Details for {selected_food_name}")
                st.dataframe(nutrient_df)

            else:
                st.error("Could not retrieve food details.")
        else:
            st.error("No results found. Try another search term.")
    else:
        st.warning("Please enter a food name to search.")

# Display meals
st.subheader("Your Meals")
total_carbs = {"Breakfast": 0, "Lunch": 0, "Dinner": 0}
total_protein = {"Breakfast": 0, "Lunch": 0, "Dinner": 0}
total_fat = {"Breakfast": 0, "Lunch": 0, "Dinner": 0}

for meal, items in st.session_state.meals.items():
    st.write(f"{meal}:")
    for item in items:
        st.write(f"- {item['food_name']} (Carbs: {item['carbs']}g, Protein: {item['protein']}g, Fat: {item['fat']}g)")
        total_carbs[meal] += item["carbs"]
        total_protein[meal] += item["protein"]
        total_fat[meal] += item["fat"]

# Display total nutrients for each meal and comparison with goals
st.subheader("Total Nutrients for Each Meal")
for meal in total_carbs:
    st.write(f"{meal}: Carbs: {total_carbs[meal]}g, Protein: {total_protein[meal]}g, Fat: {total_fat[meal]}g")

# Display progress bars and feedback based on goal comparison
st.subheader("Progress Towards Goals")
for nutrient, goal in zip(["Carbs", "Protein", "Fat"], [carb_goal, protein_goal, fat_goal]):
    total_nutrient = sum([total_carbs["Breakfast"], total_carbs["Lunch"], total_carbs["Dinner"]]) if nutrient == "Carbs" else \
                      sum([total_protein["Breakfast"], total_protein["Lunch"], total_protein["Dinner"]]) if nutrient == "Protein" else \
                      sum([total_fat["Breakfast"], total_fat["Lunch"], total_fat["Dinner"]])

    progress = total_nutrient / goal if goal != 0 else 0
    st.progress(min(progress, 1.0))

    if total_nutrient >= goal:
        st.success(f"Goal reached for {nutrient}!")
    else:
        st.warning(f"{nutrient} goal not reached. You need {goal - total_nutrient:.2f} more grams.")

add_custom_css()


