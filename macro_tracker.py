import streamlit as st
import requests
import pandas as pd
from matplotlib import pyplot as plt
import time
from io import BytesIO
import pyttsx3
import pythoncom
import plotly.graph_objects as go
import datetime 
from textblob import TextBlob
from transformers import pipeline

API_KEY = "c5tmsb8zUFSdHNtB4dGVeeEUyHveyggVlVdia5he"

# Load a pre-trained emotion detection model
emotion_model = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

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

def search_food(query):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": query, "api_key": API_KEY, "pageSize": 10}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

def get_food_details(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

def add_nutrient_pie_chart(total_carbs, total_protein, total_fat, carb_goal, protein_goal, fat_goal):
    labels = ['Carbs', 'Protein', 'Fat']
    values = [total_carbs, total_protein, total_fat]

    # Create a pie chart with bright colors and black background
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, 
                                 marker=dict(colors=['#FF6F61', '#6B5B95', '#F4A300']))])

    fig.update_layout(
        title="Nutrient Breakdown",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white"
    )
    st.plotly_chart(fig)

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

    # Add the pie chart for nutrient breakdown
    add_nutrient_pie_chart(total_carbs, total_protein, total_fat, carb_goal, protein_goal, fat_goal)

def add_custom_css():
    st.markdown("""
    <style>
    .card {
        background-color: #00000;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .exercise-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #00000;
    }
    .timer {
        font-size: 1.2em;
        color: #007BFF;
    }
    .progress-bar {
        height: 15px;
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def calculate_calories_burned(weight, exercise_name, minutes):
    # Simple estimation (in kcal)
    if exercise_name == "Push-ups":
        return 0.08 * weight * minutes  # Approximate calorie burn per minute
    return 0.05 * weight * minutes

def exercise_card(exercise_details, exercise_id):
    # Split the exercise details into individual components (Exercise Name, Reps, Duration, Weight)
    if ' | ' not in exercise_details:
        st.error("Invalid exercise details format. Ensure the format is 'Exercise Name | Reps | Duration | Weight'.")
        return

    try:
        exercise_name, reps, duration, weight = exercise_details.split(' | ')
    except ValueError:
        st.error("The format of the exercise details is incorrect. Please make sure it's 'Exercise Name | Reps | Duration | Weight'.")
        return

    # Extract the numeric values from the string
    try:
        reps = int(reps.split()[0])  # Get the number of reps
        duration_minutes = int(duration.split()[0])  # Get the duration in minutes
        weight = int(weight.split()[0])  # Get the weight in kg
    except ValueError:
        st.error("Reps, Duration, and Weight should be numeric values.")
        return

    # Structure the exercise content within a div (to style as a card)
    st.markdown(f'''
    <div class="card">
        <div class="exercise-title" style="color: black;">{exercise_name}</div>
        <div style="color: black;"><b>Reps:</b> {reps} | <b>Duration:</b> {duration_minutes} min | <b>Weight:</b> {weight} kg</div>
    ''', unsafe_allow_html=True)

    completed_reps = 0
    elapsed_seconds = 0
    calories_burned = 0

    # Start timer progress
    progress_bar = st.progress(0)

    # Timer countdown (no time numbers printed)
    while elapsed_seconds < duration_minutes * 60:  # Convert duration to seconds
        # Simulate time passing by one second
        time.sleep(1)
        elapsed_seconds += 1

        # Track calories burned
        calories_burned = calculate_calories_burned(weight, exercise_name, elapsed_seconds / 60)

        # Update the progress bar (represent the remaining time)
        progress_percentage = ((duration_minutes * 60 - elapsed_seconds) / (duration_minutes * 60)) * 100
        progress_bar.progress(int(progress_percentage))

    # Completion Message after the timer reaches 0
    st.markdown(f'''
        <div class="timer" style="color: white;">Exercise Completed! Calories Burned: {calories_burned:.2f} kcal</div>
    ''', unsafe_allow_html=True)

    # Add buttons for removing the exercise
    if st.button(f"Remove {exercise_name}", key=exercise_id):
        st.session_state.exercises = [exercise for exercise in st.session_state.exercises if exercise["id"] != exercise_id]

    # Close the card div
    st.markdown('</div>', unsafe_allow_html=True)

    return calories_burned

def exercise_tracker():
    add_custom_css()
    st.header("Exercise Tracker")

    # Session state for exercises and calories burned
    if "exercises" not in st.session_state:
        st.session_state.exercises = []
    if "calories_burned_data" not in st.session_state:
        st.session_state.calories_burned_data = {}

    # Add new exercise form
    with st.form("add_exercise"):
        st.header("Add a Exercise")
        
        # Exercise Name input and additional details
        exercise_name = st.text_input("Exercise Name", value="Push-ups")
        total_reps = st.number_input("Total Reps", min_value=1, value=10, step=1)
        duration_minutes = st.number_input("Duration (in minutes)", min_value=1, value=1, step=1)
        weight = st.number_input("Your Weight (kg)", min_value=1, value=70)

        # Ensure the formatted string is correct (Reps, Duration, Weight, and Exercise Name are included)
        if not exercise_name or not total_reps or not duration_minutes or not weight:
            st.error("Please provide all the fields (Exercise Name, Reps, Duration, Weight).")
        else:
            formatted_exercise_name = f"{exercise_name} | {total_reps} Reps | {duration_minutes} min | {weight} kg"
            
            # Add exercise button
            add_exercise = st.form_submit_button("Add Exercise")

            if add_exercise:
                exercise_id = len(st.session_state.exercises) + 1
                st.session_state.exercises.append({
                    "id": exercise_id,
                    "name": formatted_exercise_name,
                    "reps": total_reps,
                    "duration_seconds": duration_minutes * 60,  # Store in seconds for easier time calculations
                    "weight": weight
                })
                st.success(f"Added {exercise_name} successfully!")

    # Display all added exercises in card format and track calories
    total_calories_burned = 0
    exercise_names = []
    calories_values = []

    if st.session_state.exercises:
        for exercise in st.session_state.exercises:
            # Call exercise_card and get the calories burned for each exercise
            calories_burned = exercise_card(
                exercise["name"],
                exercise["id"]
            )

            # Track calories for pie chart
            exercise_names.append(exercise["name"])
            calories_values.append(calories_burned)

            # Update the total calories burned
            total_calories_burned += calories_burned

    st.header("Workout Suggestions")
    
    # Workout type selection
    workout_type = st.radio(
        "Choose a workout type:",
        ["Strength", "Cardio", "Full-body"]
    )
    
    # Workout database
    workout_database = {
        "Strength": ["Push-ups", "Squats", "Deadlifts", "Lunges", "Plank"],
        "Cardio": ["Running", "Cycling", "Jump Rope", "Burpees", "Swimming"],
        "Full-body": ["Jumping Jacks", "Mountain Climbers", "Burpees", "Lunges", "Push-ups"]
    }
    
    # Displaying suggested exercises based on workout type
    st.subheader(f"Suggested {workout_type} Exercises")
    for exercise in workout_database[workout_type]:
        st.write(f"- {exercise}")
    
    # Difficulty level selection
    difficulty = st.selectbox("Select workout difficulty:", ["Beginner", "Intermediate", "Advanced"])
    
    # Display suggested sets and reps based on difficulty level
    if difficulty == "Beginner":
        reps_sets = {
            "Strength": {"Push-ups": "3 sets of 8-10 reps", "Squats": "3 sets of 10-12 reps", "Deadlifts": "3 sets of 6-8 reps", 
                         "Lunges": "3 sets of 10 reps per leg", "Plank": "3 sets of 20-30 seconds"},
            "Cardio": {"Running": "15-20 minutes at a moderate pace", "Cycling": "20-30 minutes at a comfortable pace", 
                       "Jump Rope": "3 sets of 30 seconds", "Burpees": "3 sets of 5-10 reps", "Swimming": "15-20 minutes easy swim"},
            "Full-body": {"Jumping Jacks": "3 sets of 30 seconds", "Mountain Climbers": "3 sets of 20-30 reps", 
                          "Burpees": "3 sets of 5-10 reps", "Lunges": "3 sets of 10 reps per leg", "Push-ups": "3 sets of 8-10 reps"}
        }
        
    elif difficulty == "Intermediate":
        reps_sets = {
            "Strength": {"Push-ups": "4 sets of 12-15 reps", "Squats": "4 sets of 15-20 reps", "Deadlifts": "4 sets of 10-12 reps", 
                         "Lunges": "4 sets of 12 reps per leg", "Plank": "4 sets of 45 seconds"},
            "Cardio": {"Running": "25-30 minutes at a moderate pace", "Cycling": "30-40 minutes at a steady pace", 
                       "Jump Rope": "4 sets of 45 seconds", "Burpees": "4 sets of 10-15 reps", "Swimming": "30 minutes moderate intensity swim"},
            "Full-body": {"Jumping Jacks": "4 sets of 45 seconds", "Mountain Climbers": "4 sets of 30-40 reps", 
                          "Burpees": "4 sets of 10-15 reps", "Lunges": "4 sets of 12 reps per leg", "Push-ups": "4 sets of 12-15 reps"}
        }
        
    elif difficulty == "Advanced":
        reps_sets = {
            "Strength": {"Push-ups": "5 sets of 20 reps", "Squats": "5 sets of 20-25 reps", "Deadlifts": "5 sets of 12-15 reps", 
                         "Lunges": "5 sets of 20 reps per leg", "Plank": "5 sets of 1 minute"},
            "Cardio": {"Running": "30-45 minutes at a fast pace", "Cycling": "40-60 minutes at a challenging pace", 
                       "Jump Rope": "5 sets of 1 minute", "Burpees": "5 sets of 15-20 reps", "Swimming": "40 minutes high-intensity swim"},
            "Full-body": {"Jumping Jacks": "5 sets of 1 minute", "Mountain Climbers": "5 sets of 50 reps", 
                          "Burpees": "5 sets of 15-20 reps", "Lunges": "5 sets of 20 reps per leg", "Push-ups": "5 sets of 20 reps"}
        }
    
    # Display sets and reps for each exercise
    st.subheader(f"Reps and Sets for {difficulty} Level")
    for exercise in workout_database[workout_type]:
        st.write(f"- {exercise}: {reps_sets[workout_type].get(exercise)}")
    
    # Display difficulty level
    st.write(f"Suggested difficulty: {difficulty}")

    # Plot Pie Chart comparing calories burned by each exercise
    if exercise_names:
        fig = go.Figure(data=[go.Pie(
            labels=exercise_names,
            values=calories_values,
            hole=0.3,
            marker=dict(colors=['#FF6F61', '#6B5B95', '#F4A300', '#56A5D8'])
        )])

        fig.update_layout(
            title="Calories Burned per Exercise",
            plot_bgcolor="black",
            paper_bgcolor="black",
            font_color="white"
        )
        st.plotly_chart(fig)

def add_custom_css():
    st.markdown("""
    <style>
    .card {
        background-color: #f4f4f4;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .exercise-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
    }
    .timer {
        font-size: 1.2em;
        color: #007BFF;
    }
    .progress-bar {
        height: 15px;
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def add_custom_css():
    st.markdown("""
    <style>
    .card {
        background-color: #f4f4f4;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .exercise-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
    }
    .timer {
        font-size: 1.2em;
        color: #007BFF;
    }
    .progress-bar {
        height: 15px;
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def speak(text):

    pythoncom.CoInitialize()

    engine = pyttsx3.init("sapi5")
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
    engine.say(text)
    engine.runAndWait()
    pythoncom.CoUninitialize()  # Uninitialize COM after the speech is done

def meditation_script():
    script_parts = [
        "Welcome to your guided meditation session. Let's take this time to relax, focus, and calm your mind.",
        "Begin by finding a comfortable seat. Close your eyes, relax your body, and take a deep breath.",
        "Inhale slowly through your nose for a count of four... 1... 2... 3... 4...",
        "Now hold your breath for a moment... 1... 2... 3... 4...",
        "Exhale slowly through your mouth for a count of six... 1... 2... 3... 4... 5... 6...",
        "Repeat this breathing pattern at your own pace. Inhale for four... hold for four... and exhale for six...",
        "As you breathe in, feel your body becoming more relaxed. And as you breathe out, let go of any tension.",
        "With each breath, feel yourself becoming more at peace. Imagine each breath bringing a wave of calmness to your body.",
        "As you continue to breathe slowly and deeply, let go of any thoughts or worries. Inhale peace and exhale stress.",
        "If your mind begins to wander, gently guide it back to your breath. There's no need to judge your thoughts, simply acknowledge them and return your focus to your breath.",
        "Continue this practice for a few more minutes. Relax, breathe, and allow yourself to just be.",
        "Inhale... Exhale...",
        "You are doing great. Keep breathing deeply and stay present in this moment.",
        "When you're ready, slowly begin to bring your awareness back to the space around you. Wiggle your fingers and toes, gently opening your eyes.",
        "Take a moment to appreciate this time you've taken for yourself. You are relaxed, calm, and centered.",
        "Thank you for taking this time to nurture your mind and spirit. You are strong, and you deserve peace."
    ]
    return script_parts

def analyze_sentiment(entry):
    # Create a TextBlob object
    blob = TextBlob(entry)
    
    # Get the sentiment polarity (-1 to 1)
    sentiment = blob.sentiment.polarity
    
    if sentiment > 0:
        mood = "Positive"
    elif sentiment < 0:
        mood = "Negative"
    else:
        mood = "Neutral"
    
    # Return mood and sentiment score
    return mood, sentiment

def add_custom_css():
    st.markdown("""
    <style>
    .card {
        background-color: #f4f4f4;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .exercise-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
    }
    .timer {
        font-size: 1.2em;
        color: #007BFF;
    }
    .progress-bar {
        height: 15px;
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def mental_health_support():
    # Add custom CSS for styling
    add_custom_css()

    # Title of the page
    st.title("Meditation & Mental Health Support")

    # Display the meditation instructions and script
    st.markdown("""
    ## Welcome to the Guided Meditation Exercise

    Please follow the instructions below for a calming meditation session. 
    We will guide you through this peaceful moment.
    """)

    # Provide user with an option to start the session
    start_button = st.button("Start Meditation")

    if start_button:
        # Show progress bar for meditation duration
        duration_minutes = 5
        progress_bar = st.progress(0)
        elapsed_seconds = 0
        total_parts = len(meditation_script())
        part_duration = (duration_minutes * 60) // total_parts

        # Meditation script in smaller parts
        script_parts = meditation_script()

        # Loop through the meditation script in chunks
        for i, part in enumerate(script_parts):
            # Generate speech from the meditation script
            speak(part)

            # Update the progress bar
            elapsed_seconds += part_duration
            progress_percentage = (elapsed_seconds / (duration_minutes * 60)) * 100
            progress_bar.progress(int(progress_percentage))

            # Simulate a short delay between parts
            time.sleep(part_duration)  # Allow for a small pause between parts

        # Completion message
        st.markdown("""
        ### Meditation Completed!
        You have successfully completed your meditation session. You are relaxed and calm. 
        Take a moment to reflect on how you feel.
        """)

    st.subheader("Mental Health Journal")
    journal_entry = st.text_area("Write your thoughts for today:", "")
    
    if journal_entry:
        # Get today's date using Python's datetime module
        current_date = datetime.datetime.now().date()  # Get today's date
        
        # Analyze the sentiment of the journal entry
        mood, sentiment_score = analyze_sentiment(journal_entry)
        
        # Create a dictionary or log entry
        mental_health_data = {
            "date": str(current_date),  # Save the current date as a string
            "journal_entry": journal_entry,
            "mood": mood,
            "sentiment_score": sentiment_score
        }
        
        # You can display the journal entry and sentiment
        st.write(f"Journal entry for {current_date}:")
        st.write(mental_health_data['journal_entry'])
        st.write(f"Sentiment: {mental_health_data['mood']} (Sentiment score: {mental_health_data['sentiment_score']:.2f})")
        
        # Optionally save the entry to a session state or file (e.g., CSV or database)
        if "mental_health_entries" not in st.session_state:
            st.session_state.mental_health_entries = []
        
        # Save the journal entry
        st.session_state.mental_health_entries.append(mental_health_data)
        
        # Confirm the entry has been saved
        st.success(f"Your journal entry for {current_date} has been saved.")
        
    # Display all previous journal entries if available
    if "mental_health_entries" in st.session_state:
        st.subheader("Previous Journal Entries")
        for entry in st.session_state.mental_health_entries:
            st.write(f"Date: {entry['date']}")
            st.write(f"Entry: {entry['journal_entry']}")
            st.write("---")

# Function to detect emotion in the user's input
def detect_emotion(input_text):
    result = emotion_model(input_text)
    return result[0]['label']

# Chat function
def chatbot_response(input_text):
    emotion = detect_emotion(input_text)
    
    if emotion == "joy":
        return "I'm glad to hear you're feeling happy! 😊 How can I help you today?"
    elif emotion == "anger":
        return "I'm sorry you're feeling angry. Would you like to talk about what's bothering you?"
    elif emotion == "fear":
        return "It sounds like you're feeling fearful. Take a deep breath, and know you're not alone."
    elif emotion == "sadness":
        return "I'm really sorry you're feeling down. It’s okay to feel sad sometimes. How can I support you?"
    elif emotion == "surprise":
        return "It sounds like something unexpected has happened. Want to talk about it?"
    else:
        return "I'm here to listen. Can you tell me more about how you're feeling?"

def chatbot():
    st.title("Chat Support")
    st.write("Welcome to the chatbot! How are you feeling today? You can talk to me about anything.")

    user_input = st.text_input("Ask me a question about your mental health:")

    if user_input:
        # Get chatbot's response
        response = chatbot_response(user_input)
        st.write(f"Chatbot: {response}")
    
def other_tracker():
    st.header("Sleep Tracker")
    
    # Input for users to log sleep hours
    sleep_hours = st.number_input("How many hours did you sleep last night?", min_value=0.0, max_value=24.0, step=0.5)
    
    # Set a default sleep goal (you could also make this user-adjustable)
    sleep_goal = 8.0  # 8 hours of sleep
    
    # Load sleep data into DataFrame from CSV if exists
    try:
        sleep_df = pd.read_csv("sleep_data.csv")
    except FileNotFoundError:
        sleep_df = pd.DataFrame(columns=["date", "sleep_hours"])
    
    if st.button("Log Sleep"):
        # Get the current date using Python's datetime module
        current_date = datetime.datetime.now().date()  # Get the current date
        
        # Add new entry to DataFrame
        new_entry = pd.DataFrame([{
            "date": str(current_date),  # Store the date as a string
            "sleep_hours": sleep_hours
        }])
        sleep_df = pd.concat([sleep_df, new_entry], ignore_index=True)
        
        # Save updated DataFrame to CSV
        sleep_df.to_csv("sleep_data.csv", index=False)
        
        st.success(f"Your sleep for {str(current_date)} has been logged.")
    
    # Display previous sleep data
    if not sleep_df.empty:
        st.subheader("Previous Sleep Data")
        total_sleep = sleep_df["sleep_hours"].sum()
        st.write(f"Total hours slept: {total_sleep} hours")
        
        # Avoid division by zero: check if there are sleep entries
        if len(sleep_df) > 0:
            average_sleep = total_sleep / len(sleep_df)
            st.write(f"Average sleep: {average_sleep:.2f} hours")
        
        # Sleep goal progress
        st.write(f"Sleep Goal: {sleep_goal} hours per night")
        st.progress(min(total_sleep / (sleep_goal * len(sleep_df)), 1.0))

    st.header("Water Intake Tracker")
    
    # Load water data into DataFrame from CSV if exists
    try:
        water_df = pd.read_csv("water_data.csv")
    except FileNotFoundError:
        water_df = pd.DataFrame(columns=["date", "water_intake"])
    
    # Input for daily water intake
    water_intake = st.number_input("Enter the amount of water you drank today (in liters)", 
                                  min_value=0.0, value=0.0, step=0.1)
    
    # Set the daily water intake goal (in liters)
    water_goal = st.number_input("Set your daily water intake goal (in liters)", 
                                 min_value=0.0, value=2.0, step=0.1, max_value=10.0)
    
    # Log water intake data if the button is pressed
    if st.button("Log Water Intake"):
        # Get the current date
        current_date = str(datetime.date.today())
        
        # Add new entry to DataFrame
        new_entry = pd.DataFrame([{
            "date": current_date,
            "water_intake": water_intake
        }])
        water_df = pd.concat([water_df, new_entry], ignore_index=True)
        
        # Save updated DataFrame to CSV
        water_df.to_csv("water_data.csv", index=False)
        
        st.success(f"Your water intake for {current_date} has been logged.")
    
    # Display previous water intake data
    if not water_df.empty:
        st.subheader("Previous Water Intake Data")
        total_water = water_df["water_intake"].sum()
        st.write(f"Total water intake: {total_water:.2f} liters")
        st.write(f"Average water intake: {total_water / len(water_df):.2f} liters")
        
        # Water goal progress
        st.write(f"Water Goal: {water_goal} liters")
        st.progress(min(total_water / (water_goal * len(water_df)), 1.0))

def main():
    """Main app function with tabs including the Chat Support page."""
    st.set_page_config(page_title="Fitness Tracker", layout="wide")
    add_custom_css()

    # Tabs for navigation at the top
    tabs = st.tabs(["**Macro Tracker**", "Excercise Tracker", "Mental Health Support", "Chat Support", "Other Tackers"])

    with tabs[0]:
        macro_tracker()
    with tabs[1]:
        exercise_tracker()
    with tabs[2]:
        mental_health_support()
    with tabs[3]:
        chatbot()
    with tabs[4]:
        other_tracker()   

if __name__ == "__main__":
    main()

