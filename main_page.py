import streamlit as st
import sqlite3
import time
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

# SQLite connection
conn = sqlite3.connect('fitness_app.db')
c = conn.cursor()

# Create users table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()

# CSS Styling
def local_css():
    st.markdown("""<style>/* custom styles here */</style>""", unsafe_allow_html=True)
local_css()

# Add calories after countdown
def count_down(seconds, calories_to_add):
    countdown_placeholder = st.empty()
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        countdown_placeholder.markdown(f"<h1 style='color:#08c2af;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    countdown_placeholder.markdown("<h2 style='color:#94d2bd;'>Time's Up! 🎉</h2>", unsafe_allow_html=True)
    st.session_state.calories_burned = st.session_state.get('calories_burned', 0) + calories_to_add

# Add calories instantly
def only_cal(calories_to_add):
    st.session_state.calories_burned = st.session_state.get('calories_burned', 0) + calories_to_add

# User login/signup
def login():
    st.markdown("<h1 class='title'>🏋️‍♂️ Welcome to <span style='color:#94d2bd;'>FitPal</span></h1>", unsafe_allow_html=True)
    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])

    if "signedout" not in st.session_state:
        st.session_state.signedout = False
    if "signout" not in st.session_state:
        st.session_state.signout = False

    def do_login():
        try:
            user = auth.get_user_by_email(email)
            st.success("Login Successful")
            st.session_state.update({
                "Username": user.uid,
                "Useremail": user.email,
                "signedout": True,
                "signout": True,
                "page": "Workout"
            })
        except:
            st.warning("Login Failed")

    def do_logout():
        st.session_state.update({
            "signedout": False,
            "signout": False,
            "Username": ""
        })

    if not st.session_state.signedout:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        username = st.text_input("Username" if choice == 'Login' else "Create Username")

        if choice == 'Login':
            st.button("Login", on_click=do_login)
        else:
            if st.button("Create Account"):
                auth.create_user(email=email, password=password, uid=username)
                st.success("Account Created Successfully!")

    if st.session_state.signout:
        st.text("Name: " + st.session_state.Username)
        st.button("Sign Out", on_click=do_logout)

# Main navigation
def main():
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0

    page = st.sidebar.radio("Navigate", ("Home", "Goal", "Workout", "Calories", "BMI", "Recipes", "About"))

    if page == "Home":
        login()
    elif page == "Goal":
        goal = st.selectbox("Select your fitness goal:", ["Gain Weight", "Lose Weight"])
        st.session_state.goal = goal.lower()
        st.success(f"You chose to {goal.lower()}!")
    elif page == "Workout":
        handle_workout_page()
    elif page == "Calories":
        show_calories()
    elif page == "BMI":
        bmi_calculator()
    elif page == "Recipes":
        show_recipes()
    elif page == "About":
        show_about()

# Workout logic
def handle_workout_page():
    # similar to your current function (can be split further if needed)
    pass

# Calories display
def show_calories():
    burned = st.session_state.calories_burned
    st.markdown(f"<h3>Total Calories Burned: <span style='color:#94d2bd'>{burned}</span></h3>", unsafe_allow_html=True)
    st.progress(min(burned / 600, 1.0))
    if burned >= 600:
        st.success("Goal achieved! 🎉")

# BMI Calculator
def bmi_calculator():
    weight = st.slider("Weight (kg):", 10, 200)
    height = st.slider("Height (cm):", 90, 250)
    bmi = weight / ((height / 100) ** 2)
    st.markdown(f"<h3>Your BMI: <span style='color:#94d2bd'>{bmi:.2f}</span></h3>", unsafe_allow_html=True)

# Recipes section
def show_recipes():
    # logic as in your code
    pass

# About section
def show_about():
    st.markdown("<h2 style='color:#08c2af;'>📖 About FitPal</h2>", unsafe_allow_html=True)
    st.markdown("FitPal is a student-built fitness tracker with workouts, goals, calories, BMI, and healthy recipes.")

if __name__ == "__main__":
    main()
    conn.close()


