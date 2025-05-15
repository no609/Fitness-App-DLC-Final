import streamlit as st
import sqlite3
import time
import os
import dotenv
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import time








# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)
conn = sqlite3.connect('fitness_app.db')
c = conn.cursor()

# Create a table for storing user information if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()



os.makedirs('.streamlit', exist_ok=True)
with open('.streamlit/config.toml', 'w') as f:
     f.write('''[theme]
primaryColor = "#08c2af"
backgroundColor = "#002b36"
secondaryBackgroundColor = "#586e75"
textColor = "#ffffff"

[client]
toolbarMode = "minimal"
''')

# Streamlit page config
st.set_page_config(
    page_title="FitPal - Your Fitness Companion",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styles for beautifying the app
def local_css():
    st.markdown(
        """
        <style>
        /* Background gradient */
        .main {
            background: linear-gradient(135deg, #0a9396, #94d2bd);
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        /* Header styling */
        .title {
            font-weight: 900;
            font-size: 3rem !important;
            color: #e9d8a6;
            letter-spacing: 2px;
            text-shadow: 2px 2px 4px #00000055;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #005f73;
            color: white;
            font-size: 1.1rem;
        }

        /* Button styling */
        div.stButton > button:first-child {
            background-color: #0a9396;
            color: white;
            font-weight: 700;
            border-radius: 10px;
            padding: 10px 24px;
            border: none;
            transition: background-color 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #94d2bd;
            color: #005f73;
            cursor: pointer;
        }

        /* Checkbox label color */
        .stCheckbox > label {
            color: white !important;
            font-size: 1rem;
            font-weight: 600;
        }

        /* Text input style */
        div.stTextInput > div > input {
            border-radius: 8px;
            padding: 8px;
            border: 2px solid #0a9396;
            color: #001219;
            font-weight: 700;
        }

        /* Markdown text color */
        .css-1kyxreq p, .css-1kyxreq span {
            color: white;
        }
        /* Progress bar color */
        .stProgress > div > div > div > div {
            background-color: #94d2bd !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

local_css()

# Countdown timer with calories update
def count_down(seconds: int, calories_to_add: int):
    countdown_placeholder = st.empty()
    
    with st.spinner("Workout in progress... Keep Going!"):
        for remaining in range(seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            time_now = f'{mins:02d}:{secs:02d}'
            
            countdown_placeholder.header(f"⏳ Time Left: {time_now}")
            time.sleep(1)
            
    countdown_placeholder.header("🎉 Time's Up! Great Job! 🎉")
    
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories_to_add

def only_cal(calories_to_add: int):
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories_to_add

# Navigation helper to redirect user to a different page
def navigate_to(page_name):
    st.session_state.current_page = page_name

# Authentication page
def login():
    st.markdown("<h1 class='title'>🏋️‍♂️ Welcome to <span style='color:#94d2bd;'>FitPal</span></h1>", unsafe_allow_html=True)
    st.markdown("""
        <p style='font-size:1.25rem;'>
        Your ultimate fitness companion app! Get motivated, track progress, and achieve your goals in style.
        </p>
        <hr style="border: 1px solid #94d2bd; margin-bottom: 20px;">
    """, unsafe_allow_html=True)
    
    if "Username" not in st.session_state:
        st.session_state.Username = ""
    if "Useremail" not in st.session_state:
        st.session_state.Useremail = ""

    if "signedout" not in st.session_state:
        st.session_state.signedout = False
    if "signout" not in st.session_state:
        st.session_state.signout = False

    # Login callback
    def login_user(email, password):
        try:
            user = auth.get_user_by_email(email)
            # Note: Password authentication not implemented fully here due to Firebase Admin limitations in this context
            st.success(f"Login Successful! Welcome, {user.uid}")
            st.session_state.Username = user.uid
            st.session_state.Useremail = user.email
            st.session_state.signedout = True
            st.session_state.signout = True
            st.session_state.current_page = "Workout"
        except Exception as e:
            st.error(f"Login Failed: {e}")

    # Signout callback
    def sign_out():
        st.session_state.signedout = False
        st.session_state.signout = False
        st.session_state.Username = ""
        st.session_state.Useremail = ""
        st.success("You have signed out successfully!")
        st.session_state.current_page = "Home"

    choice = st.radio('Choose an option:', ['Login', 'Sign Up'], horizontal=True)

    if not st.session_state.signedout:
        if choice == 'Login':
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    login_user(email, password)
        else:
            with st.form("signup_form", clear_on_submit=False):
                email = st.text_input("Your Email")
                password = st.text_input("Create Password", type="password")
                username = st.text_input("Desired Username")
                submitted = st.form_submit_button("Create Account")
                if submitted:
                    try:
                        user = auth.create_user(email=email, password=password, uid=username)
                        st.success("Account Created Successfully!")
                        st.info("Please login using your credentials.")
                    except Exception as e:
                        st.error(f"Account Creation Failed: {e}")

    if st.session_state.signout:
        st.subheader(f"Logged in as: {st.session_state.Username}")
        if st.button("Sign Out"):
            sign_out()

# Goal selection page
def goal_selection():
    st.title("🎯 Set Your Fitness Goal")
    goals = ["Lose Weight", "Gain Muscle"]

    # Ensure that the goal is initialized in session state
    if "goal" not in st.session_state or st.session_state.goal not in goals:
        st.session_state.goal = goals[0]  # Default to the first goal

    # Use the current goal or default to the first goal
    selected_goal = st.selectbox("Choose your goal:", goals, index=goals.index(st.session_state.goal))
    st.session_state.goal = selected_goal
    st.success(f"Your goal is set to: {selected_goal}")
    st.button("Go to Workout Plan", on_click=lambda: navigate_to("Workout"))

# Workout page
def workout_plan():
    if 'goal' not in st.session_state:
        st.warning("Please set your fitness goal first in the 'Goal' page!")
        return

    st.title(f"💪 Workout Plan to {st.session_state.goal}")

    # Timer Session State Setup
    if "timer_started" not in st.session_state:
        st.session_state.timer_started = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "timer_done" not in st.session_state:
        st.session_state.timer_done = False

    # Timer Controls
    col1, col2 = st.columns([3,1])
    with col1:
        start_workout = st.checkbox("Start Workout Timer", value=st.session_state.timer_started)
    with col2:
        if start_workout:
            if not st.session_state.timer_started:
                st.session_state.start_time = time.time()
                st.session_state.timer_started = True
                st.session_state.timer_done = False
        else:
            st.session_state.timer_started = False
            st.session_state.timer_done = False

    if st.session_state.timer_started and not st.session_state.timer_done:
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, 3600 - elapsed)
        minutes, seconds = divmod(remaining, 60)
        st.info(f"⏰ Workout Time Remaining: {int(minutes):02d}:{int(seconds):02d}")
        if remaining == 0:
            st.session_state.timer_done = True
            st.success("🎉 Time's up! Keep it up!")
    elif not st.session_state.timer_started:
        st.write("⏸ Start your timer to track the workout.")

    # Exercises based on goal
    exercises_get = {
        "Lose Weight": {
            "Burpee": [10,12,14],
            "Pushups": [10,12,14],
            "Squats": [10,12,14],
            "Joggings (1 Hour)": [1],
            "Plank": [30, 45, 60],  # seconds
            "Jump Squats": [10,12,14],
            "Mountain Climber": [10,12,14],
            "Skipping (30 Minutes)": [1],
            "Jumping Jacks": [10,12,14]
        },
        "Gain Muscle": {
            "Pushups": [10,12,14],
            "Pullups": [10,12,14],
            "Squats": [10,12,14],
            "Lunges": [10,12,14],
            "Plank": [30, 45, 60],
            "Jump Squats": [10,12,14],
            "Crunches": [10,12,14],
            "Jumping Jacks": [10,12,14]
        },
    }

    exercises = exercises_get.get(st.session_state.goal, {})

    # Organize and display each exercise with checkboxes
    for exercise, reps_list in exercises.items():
        st.markdown(f"### 🏋️ {exercise}")
        cols = st.columns(len(reps_list))
        for i, rep in enumerate(reps_list):
            label = f"{rep} {'Seconds' if exercise.lower()=='plank' or 'joggings' in exercise.lower() or 'skipping' in exercise.lower() else 'Reps'}"
            # Unique key for each checkbox
            key = f"{exercise}_{rep}"
            if cols[i].checkbox(label, key=key):
                only_cal(10)
    st.markdown("---")

    # Button to redirect to Calories burned page
    if st.button("Check Calories Burned"):
        navigate_to("Calories")

# Calories burned page with progress and chart
def calories_page():
    st.title("🔥 Calories Burned Tracker")

    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    
    calories = st.session_state.calories_burned
    daily_goal = 600

    st.metric(label="Calories Burned Today", value=f"{calories} kcal")
    progress = min(calories / daily_goal, 1.0)
    st.progress(progress)

    if calories >= daily_goal:
        st.balloons()
        st.success("🎉 Congratulations! You've reached your daily calorie burn goal! 🎉")
    else:
        remaining = daily_goal - calories
        st.info(f"Keep going! Only {remaining} kcal left to reach your goal!")

    # Historical calories data simulation
    if "calories_history" not in st.session_state:
        st.session_state.calories_history = [0]

    # Append current calories to history (simulate daily accumulation)
    if st.session_state.calories_history[-1] != calories:
        st.session_state.calories_history.append(calories)

    # Display a line chart of calorie burn progress
    df = pd.DataFrame({"Calories Burned": st.session_state.calories_history})
    st.line_chart(df)

    # Quick navigation button
    st.button("Go to Workout Plan", on_click=lambda: navigate_to("Workout"))

# BMI Calculator page
def bmi_calculator():
    st.title("📏 Body Mass Index (BMI) Calculator")

    weight = st.slider("Weight (kg):", min_value=10, max_value=200, value=70)
    height = st.slider("Height (cm):", min_value=90, max_value=230, value=170)
    bmi = weight / ((height / 100) **2)
    st.markdown(f"### Your BMI is: {bmi:.2f}")

    st.markdown("""
    **BMI Categories:**
    - Underweight: less than 18.5
    - Normal weight: 18.5 - 24.9
    - Overweight: 25 - 29.9
    - Obesity: 30 or greater
    """)

    if bmi < 18.5:
        st.warning("You are underweight. Consider consulting a healthcare professional.")
    elif 18.5 <= bmi < 25:
        st.success("You have a normal weight. Keep up the good work!")
    elif 25 <= bmi < 30:
        st.warning("You are overweight. A healthy diet and exercise would help.")
    else:
        st.error("You are in the obesity range. Please consult a healthcare professional.")

# Recipes page with images and descriptions
def recipes():
    st.title("🥗 Healthy Recipes")

    if 'goal' not in st.session_state:
        st.warning("Please set your fitness goal first in the 'Goal' page!")
        return

    col1, col2 = st.columns(2, gap="large")

    if st.session_state.goal == "Gain Muscle":
        with col1:
            st.image(r"./avacado.png", width=250)
            st.markdown("### Avocados: High calorie and healthy fats - great to support weight gain.")
        with col2:
            st.image(r"./eggs.png", width=250)
            st.markdown("### Eggs: Rich in protein and healthy fats, perfect for muscle building.")
    else:
        with col1:
            st.image(r"./paneer.png", width=300)
            st.markdown("### Paneer: High protein and healthy fats - supports fat loss and muscle retention.")
        with col2:
            st.image(r"./salad.png", width=300)
            st.markdown("### Salad: Low calorie and fiber rich to support weight loss.")

    st.markdown("---")
    st.button("Back to Goal Selection", on_click=lambda: navigate_to("Goal"))

# About page
def about_page():
    st.title("📖 About FitPal")
    st.markdown("""
    FitPal is a fitness tracking app developed by a team of passionate students.
    Built using Python and Streamlit, FitPal combines technology and wellness to promote healthy habits in a fun and interactive way.

    - Log workouts
    - Set personal fitness goals
    - Track calories burned and BMI
    - Access healthy recipes

    Our goal is to create a user-friendly platform that encourages people of all ages to take charge of their health.
    
    Through this project, we not only learned about programming but also about the importance of teamwork, problem-solving, and healthy living.
    """)
    st.markdown("---")
    if st.button("Back to Home"):
        navigate_to("Home")


# Main function controlling page navigation
def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    if "calories_burned" not in st.session_state:
        st.session_state.calories_burned = 0
    if "goal" not in st.session_state:
        st.session_state.goal = None

    # Sidebar for navigation with quick buttons
    with st.sidebar:
        st.markdown("<h2 style='color:#e9d8a6;'>FitPal Menu</h2>", unsafe_allow_html=True)
        if st.button("🏠 Home"):
            navigate_to("Home")
        if st.button("🎯 Goal"):
            navigate_to("Goal")
        if st.button("💪 Workout"):
            navigate_to("Workout")
        if st.button("🔥 Calories"):
            navigate_to("Calories")
        if st.button("📏 BMI Calculator"):
            navigate_to("BMI")
        if st.button("🥗 Recipes"):
            navigate_to("Recipes")
        if st.button("ℹ️ About"):
            navigate_to("About")
        st.markdown("---")
        st.markdown(f"**Current page:** {st.session_state.current_page}")

    # Render current page
    page = st.session_state.current_page

    if page == "Home":
        login()
    elif page == "Goal":
        goal_selection()
    elif page == "Workout":
        workout_plan()
    elif page == "Calories":
        calories_page()
    elif page == "BMI":
        bmi_calculator()
    elif page == "Recipes":
        recipes()
    elif page == "About":
        about_page()
    else:
        st.error("Page not found!")

if __name__ == "__main__":
    main()
    conn.close()
