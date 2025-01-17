import streamlit as st
import requests
import pandas as pd
from matplotlib import pyplot as plt
import time

# Define your API Key here
API_KEY = "your_usda_api_key_here"

# Add custom CSS for styling
def add_custom_css():
    st.markdown("""
        <style>
        .card {
            background-color: #1ABC9C;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            color: white;
            font-family: 'Poppins', sans-serif;
            text-align: center;
            margin: 20px auto;
            max-width: 400px;
        }
        .exercise-title {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .timer {
            font-size: 2em;
            font-weight: bold;
            color: #fefefe;
            margin: 20px 0;
        }
        .card-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
        }
        .add-button, .remove-button {
            font-size: 1.5em;
            font-weight: bold;
            color: white;
            background-color: #E74C3C;
            border: none;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
        }
        .add-button:hover, .remove-button:hover {
            background-color: #C0392B;
        }
        </style>
    """, unsafe_allow_html=True)

# Search food using USDA API
def search_food(query):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": query, "api_key": API_KEY, "pageSize": 10}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Get details of the food item from the USDA API
def get_food_details(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Macro Tracker
def macro_tracker():
    st.header("Macro Tracker")
    # Sidebar for macro goals
    st.sidebar.header("Set Macro Goals")
    carb_goal = st.sidebar.number_input("Carbs Goal (g)", value=150)
    protein_goal = st.sidebar.number_input("Protein Goal (g)", value=100)
    fat_goal = st.sidebar.number_input("Fat Goal (g)", value=50)

    if "meals" not in st.session_state:
        st.session_state.meals = {"Breakfast": [], "Lunch": [], "Dinner": []}

    meal_category = st.selectbox("Select Meal Category", ["Breakfast", "Lunch", "Dinner"])
    food_query = st.text_input("Enter a food name", placeholder="e.g., chicken breast")

    if st.button("Search Food"):
        if food_query:
            search_results = search_food(food_query)
            if search_results and "foods" in search_results:
                food_items = search_results["foods"]
                food_options = {food["description"]: food["fdcId"] for food in food_items}
                selected_food_name = st.selectbox("Select a food", list(food_options.keys()))
                selected_fdc_id = food_options[selected_food_name]

                food_details = get_food_details(selected_fdc_id)
                if food_details:
                    nutrients = food_details.get("foodNutrients", [])
                    carbs = protein = fat = 0
                    for nutrient in nutrients:
                        name = nutrient.get("nutrient", {}).get("name", "").lower()
                        if "carbohydrate" in name:
                            carbs = nutrient.get("amount", 0)
                        elif "protein" in name:
                            protein = nutrient.get("amount", 0)
                        elif "fat" in name:
                            fat = nutrient.get("amount", 0)

                    st.session_state.meals[meal_category].append({
                        "food_name": selected_food_name,
                        "carbs": carbs,
                        "protein": protein,
                        "fat": fat
                    })

    st.subheader("Meals Summary")
    total_carbs, total_protein, total_fat = 0, 0, 0
    for meal, items in st.session_state.meals.items():
        st.write(f"**{meal}**:")
        for item in items:
            st.write(f"- {item['food_name']} (Carbs: {item['carbs']}g, Protein: {item['protein']}g, Fat: {item['fat']}g)")
            total_carbs += item['carbs']
            total_protein += item['protein']
            total_fat += item['fat']

    st.subheader("Progress Towards Goals")
    for nutrient, goal, total in zip(
        ["Carbs", "Protein", "Fat"],
        [carb_goal, protein_goal, fat_goal],
        [total_carbs, total_protein, total_fat]
    ):
        progress = total / goal if goal > 0 else 0
        st.progress(min(progress, 1.0))
        st.write(f"{nutrient}: {total}g / {goal}g")

# Exercise Tracker
def exercise_card(exercise_name, total_reps, duration_seconds, exercise_id):
    # Exercise title
    st.markdown(f'<div class="card"><div class="exercise-title">{exercise_name}</div>', unsafe_allow_html=True)

    completed_reps = 0
    elapsed_seconds = 0

    while elapsed_seconds < duration_seconds and completed_reps < total_reps:
        # Update Timer and Reps Completed
        elapsed_minutes, elapsed_seconds_display = divmod(elapsed_seconds, 60)
        st.markdown(f'<div class="timer">{int(elapsed_minutes):02d}:{int(elapsed_seconds_display):02d}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="timer">Completed Reps: {completed_reps}/{total_reps}</div>', unsafe_allow_html=True)

        # Simulate reps and time
        time.sleep(1)
        elapsed_seconds += 1
        completed_reps += 1

        # Clear content for the next update
        st.empty()

    # Completion Message
    st.markdown('<div class="timer">Exercise Completed!</div>', unsafe_allow_html=True)

    # Add buttons for removing the exercise
    if st.button(f"Remove {exercise_name}", key=exercise_id):
        st.session_state.exercises = [exercise for exercise in st.session_state.exercises if exercise["id"] != exercise_id]

    st.markdown('</div>', unsafe_allow_html=True)

# Main Streamlit app
def main():
    add_custom_css()
    st.title("Fitness Tracker")

    # Tab selection using radio button
    tab = st.radio("Choose a section:", ("Exercise Tracker", "Macro Tracker"))

    # Session state for exercises
    if "exercises" not in st.session_state:
        st.session_state.exercises = []

    # Exercise Tracker
    if tab == "Exercise Tracker":
        st.header("Exercise Tracker")

        # Add new exercise form
        with st.form("add_exercise"):
            st.header("Add a New Exercise")
            exercise_name = st.text_input("Exercise Name", value="Push-ups")
            total_reps = st.number_input("Total Reps", min_value=1, value=10, step=1)
            duration_minutes = st.number_input("Duration (in minutes)", min_value=1, value=1, step=1)
            duration_seconds = int(duration_minutes * 60)

            if duration_seconds <= 0:
                st.error("Duration must be greater than 0.")
            else:
                add_exercise = st.form_submit_button("Add Exercise")

                if add_exercise:
                    exercise_id = len(st.session_state.exercises) + 1  # Unique ID for the exercise
                    st.session_state.exercises.append({
                        "id": exercise_id,
                        "name": exercise_name,
                        "reps": total_reps,
                        "duration_seconds": duration_seconds
                    })
                    st.success(f"Added {exercise_name} successfully!")

        # Display all added exercises in cards
        if st.session_state.exercises:
            for exercise in st.session_state.exercises:
                exercise_card(
                    exercise["name"],
                    exercise["reps"],
                    exercise["duration_seconds"],
                    exercise["id"]
                )

    # Macro Tracker
    elif tab == "Macro Tracker":
        macro_tracker()

# Run the app
if __name__ == "__main__":
    main()
