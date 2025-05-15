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

os.makedirs(".streamlit", exist_ok=True)

with open(".streamlit/config.toml", "w") as f:
    f.write("""\
[theme]
base = "dark"
primaryColor = "#08c2af"
backgroundColor = "#002b36"
secondaryBackgroundColor = "#586e75"
textColor = "#ffffff"
font = "sans serif"

[browser]
toolbarMode = "minimal"
""")




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







def count_down(seconds, calories_to_add):
    countdown_placeholder = st.empty()
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        countdown_placeholder.markdown(f"<h1 style='color:#08c2af; font-weight:bold;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    countdown_placeholder.markdown("<h2 style='color:#94d2bd; font-weight:bold;'>Time&#39;s Up! You Did It! 🎉</h2>", unsafe_allow_html=True)
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories_to_add

def only_cal(calories_to_add):
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories_to_add

def login():
    st.markdown(
        """
        <style>
        .title {
            font-size: 3rem;
            font-weight: 900;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.4rem;
            margin-bottom: 1rem;
            color: #94d2bd;
        }
        .divider {
            border: 1px solid #94d2bd;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
    st.markdown("<h1 class='title'>🏋️‍♂️ Welcome to <span style='color:#94d2bd;'>FitPal</span></h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your ultimate fitness companion app! Get motivated, track progress, and achieve your goals in style.</p>", unsafe_allow_html=True)
    

    if "Username" not in st.session_state:
        st.session_state.Username = ""
    if "Useremail" not in st.session_state:
        st.session_state.Useremail = ""

    if "signedout" not in st.session_state:
        st.session_state.signedout = False
    if "signout" not in st.session_state:
        st.session_state.signout = False

    def f():
        try:
            user = auth.get_user_by_email(Email)
            st.success("Login Successful")
            st.session_state.Username = user.uid
            st.session_state.Useremail = user.email
            st.session_state.signedout = True
            st.session_state.signout = True
            st.session_state.page = "Workout"
        except:
            st.warning("Login Failed")

    def t():
        st.session_state.signedout = False
        st.session_state.signout = False
        st.session_state.Username = ""

    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])

    if not st.session_state.signedout:
        if choice == 'Login':
            Email = st.text_input("Email")
            Password = st.text_input("Password", type="password")
            Username = st.text_input("Enter Username")
            st.button("Login", on_click=f)
        else:
            Email = st.text_input("Email")
            Password = st.text_input("Password", type="password")
            Username = st.text_input("Make A Unique Username")

            if st.button("Create Account"):
                user = auth.create_user(email=Email, password=Password, uid=Username)
                st.success("Account Created Successfully!")
                st.write("Login Using Email And Password")

    if st.session_state.signout:
        st.text("Name: " + st.session_state.Username)
        st.button("Sign Out", on_click=t)

def main():
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0

    page = st.sidebar.radio("Navigate", ("Home", "Goal", "Workout", "Calories", "BMI", "Recipes", "About"))

    if page == "Home":
        login()

    elif page == "Goal":
        st.markdown("<h2 style='color:#08c2af; font-weight:bold;'>🎯 Choose Your Goal</h2>", unsafe_allow_html=True)
        goal = st.selectbox("Select your fitness goal:", ["Gain Weight", "Lose Weight"])
        st.session_state.goal = goal.lower()
        st.success(f"You have chosen to {goal.lower()}!")

    elif page == "Workout":
        if 'goal' not in st.session_state:
            st.warning("Please select a goal on the 'Goal' page first.")
            return
        st.markdown("<h2 style='color:#08c2af; font-weight:bold;'>💪 Your Customized Personalized Plan</h2>", unsafe_allow_html=True)

        if "timer_started" not in st.session_state:
            st.session_state.timer_started = False
        if "start_time" not in st.session_state:
            st.session_state.start_time = None
        if "timer_done" not in st.session_state:
            st.session_state.timer_done = False

        start = st.checkbox("Start Workout")
        st.write('Keep your motivation up! Timer updates help you track progress. 🎯')

        if start and not st.session_state.timer_started:
            st.session_state.start_time = time.time()
            st.session_state.timer_started = True
            st.session_state.timer_done = False

        if st.session_state.timer_started and not st.session_state.timer_done:
            elapsed = time.time() - st.session_state.start_time
            remaining = max(0, 3600 - elapsed)
            minutes, seconds = divmod(remaining, 60)
            st.markdown(f"<h3 style='color:#94d2bd;'>Time Left: {int(minutes)}:{int(seconds):02d}</h3>", unsafe_allow_html=True)
            if remaining == 0:
                st.session_state.timer_done = True
                st.markdown("<h3 style='color:#08c2af;'>⏰ Time's up!</h3>", unsafe_allow_html=True)
        else:
            if not st.session_state.timer_started:
                st.markdown("<h3 style='color:#586e75;'>Waiting to start...</h3>", unsafe_allow_html=True)

        exercises_text_color = "#94d2bd"
        rep_calorie_value = 10

        if st.session_state.goal == "lose weight":
            st.markdown("<h3 style='color:#08c2af;'>Losing Weight Plan</h3>", unsafe_allow_html=True)
            exercises = {
                'Burpee': ["10 Reps", "12 Reps", "14 Reps"],
                'Pushups': ["10 Reps", "12 Reps", "14 Reps"],
                'Squats': ["10 Reps", "12 Reps", "14 Reps"],
                'Joggings': ["1 Hour"],
                'Plank': ["30 Seconds", "45 Seconds", "1 Minute"],
                'Jump Squats': ["10 Reps", "12 Reps", "14 Reps"],
                'Mountain Climber': ["10 Reps", "12 Reps", "14 Reps"],
                'Skipping': ["30 Minutes"],
                'Jumping Jacks': ["10 Reps", "12 Reps", "14 Reps"]
            }
        else:
            st.markdown("<h3 style='color:#08c2af;'>Gaining Weight Plan</h3>", unsafe_allow_html=True)
            exercises = {
                'Pushups': ["10 Reps", "12 Reps", "14 Reps"],
                'Pullups': ["10 Reps", "12 Reps", "14 Reps"],
                'Squats': ["10 Reps", "12 Reps", "14 Reps"],
                'Lunges': ["10 Reps", "12 Reps", "14 Reps"],
                'Plank': ["30 Seconds", "45 Seconds", "1 Minute"],
                'Jump Squats': ["10 Reps", "12 Reps", "14 Reps"],
                'Crunches': ["10 Reps", "12 Reps", "14 Reps"],
                'Jumping Jacks': ["10 Reps", "12 Reps", "14 Reps"]
            }

        for exercise, reps in exercises.items():
            st.markdown(f"<h4 style='color:{exercises_text_color};'>{exercise}</h4>", unsafe_allow_html=True)
            for rep in reps:
                key = f"{exercise}_{rep}"
                if st.checkbox(rep, key=key):
                    only_cal(rep_calorie_value)

    elif page == "Calories":
        st.markdown("<h2 style='color:#08c2af;'>🔥 Calories Burned</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3>Total Calories Burned Today: <span style='color:#94d2bd'>{st.session_state.calories_burned}</span></h3>", unsafe_allow_html=True)
        goal = 600
        progress = min(st.session_state.calories_burned / goal, 1.0)
        st.progress(progress)
        if st.session_state.calories_burned >= goal:
            st.success("Congratulations! You have reached your daily calorie goal! 🎉")

    elif page == "BMI":
        st.markdown("<h2 style='color:#08c2af;'>📏 BMI Calculator</h2>", unsafe_allow_html=True)
        weight = st.slider("What is your weight (kg):", 10, 200)
        height = st.slider("What is your height (cm):", 90, 250)
        BMI = weight / ((height / 100) ** 2)
        st.markdown(f"<h3>Your BMI is: <span style='color:#94d2bd'>{BMI:.2f}</span></h3>", unsafe_allow_html=True)

        st.markdown("""
        <h4 style='color:#08c2af;'>BMI Categories</h4>
        <ul style='color:#ffffff;'>
            <li><strong>Underweight:</strong> Less than 18.5</li>
            <li><strong>Normal weight:</strong> 18.5 - 24.9</li>
            <li><strong>Overweight:</strong> 25 - 29.9</li>
            <li><strong>Obesity:</strong> 30 or greater</li>
        </ul>
        """, unsafe_allow_html=True)

    elif page == "Recipes":
        st.markdown("<h2 style='color:#08c2af;'>🍽️ Healthy Recipes</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="small")
        if 'goal' not in st.session_state:
            st.warning("Please select a goal on the 'Goal' page first.")
            return

        if st.session_state.goal == "gain weight":
            with col1:
                st.image(r"./avacado.png", width=230)
                st.markdown("### Avocados are beneficial for weight gain due to their high calorie and healthy fat content.")
            with col2:
                st.image(r"./eggs.png", width=230)
                st.markdown("### Eggs support weight gain with high protein, healthy fats, and calorie density.")
        elif st.session_state.goal == "lose weight":
            with col1:
                st.image(r"./paneer.png", width=400)
                st.markdown("### Paneer provides good fats, is high in protein, low in carbohydrates, and aids fat management.")
            with col2:   
                st.image("./salad.png")
                st.markdown("### Salads help weight loss as they are low in calories and high in fiber.")

    elif page == "About":
        st.markdown("<h2 style='color:#08c2af;'>📖 About FitPal</h2>", unsafe_allow_html=True)
        st.markdown("""
        FitPal is a fitness tracking app developed by passionate students.
        Built on Python and Streamlit, it combines technology and wellness to promote healthy habits in a fun and interactive way.
        - Log workouts
        - Set personal fitness goals
        - Track calories burned and BMI
        - Access healthy recipes
        Our goal is to create a user-friendly platform encouraging people of all ages to manage their health effectively.
        This project also taught us the importance of teamwork, problem-solving, and healthy living.
        """)
        st.markdown("---")

if __name__ == "__main__":
    main()
    conn.close()

