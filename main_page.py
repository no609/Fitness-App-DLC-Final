import streamlit as st
import sqlite3
import time
import os
from datetime import date
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

# Set page config
st.set_page_config(page_title="FitPal", layout="wide", initial_sidebar_state="expanded")

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

# SQLite connection
conn = sqlite3.connect('fitness_app.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS workout_log (
    username TEXT,
    date TEXT,
    calories INTEGER
)''')
conn.commit()

# Functions
def count_down(seconds, calories_to_add):
    countdown_placeholder = st.empty()
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        countdown_placeholder.markdown(
            f"<h1 style='color:#08c2af; font-weight:bold;'>{mins:02d}:{secs:02d}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(1)
    countdown_placeholder.markdown("<h2 style='color:#94d2bd;'>Time’s Up! 🎉</h2>", unsafe_allow_html=True)
    update_calories(calories_to_add)

def update_calories(calories):
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories

def log_workout():
    today = str(date.today())
    c.execute("INSERT INTO workout_log VALUES (?, ?, ?)", 
              (st.session_state.Username, today, st.session_state.calories_burned))
    conn.commit()

def login():
    st.markdown("<h1 style='color:#94d2bd;'>🏋️ Welcome to FitPal</h1>", unsafe_allow_html=True)

    if "Username" not in st.session_state:
        st.session_state.Username = ""
    if "Useremail" not in st.session_state:
        st.session_state.Useremail = ""
    if "signedout" not in st.session_state:
        st.session_state.signedout = False

    def handle_login():
        try:
            user = auth.get_user_by_email(Email)
            st.success("Login Successful")
            st.session_state.Username = user.uid
            st.session_state.Useremail = user.email
            st.session_state.signedout = True
        except:
            st.warning("Login Failed")

    def handle_signout():
        st.session_state.signedout = False
        st.session_state.Username = ""

    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])

    if not st.session_state.signedout:
        Email = st.text_input("Email")
        Password = st.text_input("Password", type="password")
        Username = st.text_input("Username")

        if choice == 'Login':
            st.button("Login", on_click=handle_login)
        else:
            if st.button("Create Account"):
                user = auth.create_user(email=Email, password=Password, uid=Username)
                st.success("Account Created!")

    if st.session_state.signedout:
        st.text("Logged in as: " + st.session_state.Username)
        st.button("Sign Out", on_click=handle_signout)

def main():
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0

    page = st.sidebar.radio("Navigate", ("Home", "Goal", "Workout", "Calories", "BMI", "Recipes", "About"))

    if page == "Home":
        login()

    elif page == "Goal":
        goal = st.selectbox("Your Goal:", ["Gain Weight", "Lose Weight"])
        st.session_state.goal = goal.lower()
        st.success(f"Goal set to: {goal}")

    elif page == "Workout":
        if 'goal' not in st.session_state:
            st.warning("Select a goal first.")
            return

        st.markdown("<h2>💪 Workout Plan</h2>", unsafe_allow_html=True)
        start = st.checkbox("Start 1hr Workout Timer")

        if start and "timer_done" not in st.session_state:
            st.session_state.start_time = time.time()
            st.session_state.timer_done = False

        if "start_time" in st.session_state and not st.session_state.get("timer_done", False):
            elapsed = time.time() - st.session_state.start_time
            remaining = max(0, 3600 - elapsed)
            minutes, seconds = divmod(remaining, 60)
            st.markdown(f"<h4>Time Left: {int(minutes)}:{int(seconds):02d}</h4>", unsafe_allow_html=True)
            if remaining <= 0:
                st.session_state.timer_done = True
                st.success("Workout Complete!")
                log_workout()

        exercises = {
            "lose weight": ['Burpee', 'Pushups', 'Squats', 'Joggings', 'Plank', 'Skipping'],
            "gain weight": ['Pushups', 'Pullups', 'Squats', 'Lunges', 'Crunches', 'Jumping Jacks']
        }

        for ex in exercises[st.session_state.goal]:
            if st.checkbox(f"{ex} - 10 reps"):
                update_calories(10)

    elif page == "Calories":
        goal = 600
        st.markdown(f"<h3>Calories Burned: {st.session_state.calories_burned}</h3>", unsafe_allow_html=True)
        st.progress(min(st.session_state.calories_burned / goal, 1.0))
        if st.session_state.calories_burned >= goal:
            st.success("Goal Achieved!")

    elif page == "BMI":
        weight = st.slider("Weight (kg)", 10, 200)
        height = st.slider("Height (cm)", 90, 250)
        bmi = weight / ((height / 100) ** 2)
        st.markdown(f"<h3>Your BMI: {bmi:.2f}</h3>", unsafe_allow_html=True)

    elif page == "Recipes":
        st.markdown("### Healthy Recipes")
        col1, col2 = st.columns(2)
        if 'goal' not in st.session_state:
            st.warning("Select a goal first.")
            return

        if st.session_state.goal == "gain weight":
            with col1:
                st.image("./avacado.png", width=230)
                st.write("Avocados are great for weight gain.")
            with col2:
                st.image("./eggs.png", width=230)
                st.write("Eggs are high in protein and healthy fats.")
        else:
            with col1:
                st.image("./paneer.png", width=230)
                st.write("Paneer is high in protein, low in carbs.")
            with col2:
                st.image("./salad.png", width=230)
                st.write("Salads are low-calorie and high-fiber.")

    elif page == "About":
        st.markdown("""
        ### About FitPal  
        FitPal is a school project built with Python and Streamlit.  
        It helps users:
        - Set and track fitness goals  
        - Burn calories with guided workouts  
        - Check BMI  
        - Eat healthier with recipes  
        Built by students passionate about health and tech.
        """)

if __name__ == "__main__":
    main()
    conn.close()

