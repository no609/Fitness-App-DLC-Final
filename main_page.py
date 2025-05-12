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






if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    initialize_app(cred)
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


# Countdown function with Start and Stop Timer buttons
def count_down(seconds, calories_to_add):
    # Create a placeholder for the countdown
    countdown_placeholder = st.empty()
    
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)  # format specifiers
        time_now = '{:02d}:{:02d}'.format(mins, secs) 
        
        # Updating placeholder
        countdown_placeholder.header(f"{time_now}")
        time.sleep(1)  # Wait for 1 second
        
    countdown_placeholder.header("Time Up! You Did It!")
    
    # Update calories burned in session state
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories_to_add

def only_cal(calories_to_add):
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0
    st.session_state.calories_burned += calories_to_add

# Login function for user authentication
def login():
    st.title("🏋 FitPal")
    st.markdown("""
    <h1 style="font-family: Arial, sans-serif; font-size: 24px;">
        Welcome to <span style="color:skyblue;">Fitpal</span> A Fitness App! Let's get fit together!
    </h1>
""", unsafe_allow_html=True)

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

# Main function to handle different pages
def main():
    if 'calories_burned' not in st.session_state:
        st.session_state.calories_burned = 0

    page = st.sidebar.radio("Select Page", ("Home", "Goal", "Workout", "Calories", "BMI", "Recipes"))

    # Initialize session state for choice
    if 'choice_made' not in st.session_state:
        st.session_state.choice_made = False

    if page == "Home":
        login()

    elif page == "Goal":
        st.title("🎯 Choose Your Goal")
        if 'goal' not in st.session_state:
            st.session_state.goal = "lose"  # default choice

        goal = st.selectbox("Select your fitness goal:", ["gain", "lose"], index=["gain", "lose"].index(st.session_state.goal))
        st.session_state.goal = goal
        st.success(f"You have chosen to {goal} weight!")
        st.session_state.choice_made = True

    elif page == "Workout":
        if st.session_state.choice_made:
            st.title("💪 Your Customized Personalized Plan")
            if "timer_started" not in st.session_state:
                    st.session_state.timer_started = False
            if "start_time" not in st.session_state:
                    st.session_state.start_time = None
            if "timer_done" not in st.session_state:
                    st.session_state.timer_done = False

               # Start checkbox
            start = st.checkbox("Start Workout")
            st.write('As You Keep Doing Workouts The Timer Gets Updated To Motivate You 🎯')

               # Start the timer only once
            if start and not st.session_state.timer_started:
                    st.session_state.start_time = time.time()
                    st.session_state.timer_started = True
                    st.session_state.timer_done = False

               # Timer countdown logic
            if st.session_state.timer_started and not st.session_state.timer_done:
                    elapsed = time.time() - st.session_state.start_time
                    remaining = max(0, 3600 - elapsed)
                    minutes, seconds = divmod(remaining, 60)
                    st.write(f"Time Left: {int(minutes)}:{int(seconds):02d}")

                    if remaining == 0:
                         st.session_state.timer_done = True
                         st.write("⏰ Time's up!")
            else:
                    if not st.session_state.timer_started:
                         st.write("↓")
            if st.session_state.goal == "lose":
                st.markdown("## Losing Weight ##")
                st.markdown("<h4 style='color: green;'>Burpee</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_reps"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_reps"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_reps"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Pushups</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps"):
                    only_cal(10)
                if st.checkbox("12 Reps"):
                    only_cal(10)
                if st.checkbox("14 Reps"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Squats</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_rep"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_rep"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_rep"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Joggings</h4>", unsafe_allow_html=True)
                if st.checkbox("1 Hour", key="checkbox_10_re"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Plank</h4>", unsafe_allow_html=True)
                if st.checkbox("30 Seconds"):
                    only_cal(10)
                if st.checkbox("45 seconds"):
                    only_cal(10)
                if st.checkbox("1 Minute"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Jump Squats</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Mountain Climber</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Skipping</h4>", unsafe_allow_html=True)
                if st.checkbox("30 Minutes", key="checkbox_1"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Jumping Jacks</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_3"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox"):
                    only_cal(10)
            elif st.session_state.goal == "gain":
                st.markdown("## Gaining Weight ##")
                st.markdown("<h4 style='color: green;'>Pushups</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_reps"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_reps"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_reps"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Pullups</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps"):
                    only_cal(10)
                if st.checkbox("12 Reps"):
                    only_cal(10)
                if st.checkbox("14 Reps"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Squats</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_rep"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_rep"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_rep"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Lunges</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_re"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_re"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_re"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Plank</h4>", unsafe_allow_html=True)
                if st.checkbox("30 Seconds"):
                    only_cal(10)
                if st.checkbox("45 seconds"):
                    only_cal(10)
                if st.checkbox("1 Minute"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Jump Squats</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10_"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12_"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14_"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Crunches</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_10"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_12"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_14"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Lunges</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_1"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_2"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox_4"):
                    only_cal(10)
                st.markdown("<h4 style='color: green;'>Jumping Jacks</h4>", unsafe_allow_html=True)
                if st.checkbox("10 Reps", key="checkbox_3"):
                    only_cal(10)
                if st.checkbox("12 Reps", key="checkbox_"):
                    only_cal(10)
                if st.checkbox("14 Reps", key="checkbox"):
                    only_cal(10)
                

                
                
                
                

                    
                
            
        else:
            st.warning("Please make a choice on the 'Choice' page first.")
    
    elif page == "Calories":
        st.title("🔥 Calories Burned")
        st.write(f"Total Calories Burned Are {st.session_state.calories_burned}")
        if st.session_state.calories_burned >= 600:
            st.write("The Daily Goal Has Been Done")
        goal = 600
        progress = st.session_state.calories_burned / goal
        st.progress(progress)
    elif page == "BMI":
        st.title("📏 BMI Calculator")
        weight = st.slider("What Is Your Weight(kg): ", 10, 200)
        height = st.slider("What Is Your Height(cm): ", 90, 200)
        BMI = (weight) / ((height / 100) ** 2)
        st.write(f"Your BMI is: {BMI:.2f}")
        
        st.markdown("### BMI Categories ###")
        st.markdown("**Underweight:** Less than 18.5")
        st.markdown("**Normal weight:** 18.5 - 24.9")
        st.markdown("**Overweight:** 25 - 29.9")
        st.markdown("**Obesity:** 30 or greater")
    
    elif page == "Recipes":
        col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
        if st.session_state.choice_made:
            if st.session_state.goal == "gain":
                with col1:
                    st.image(r"./avacado.png", width=230)
                    st.markdown("### Avocados can be beneficial for weight gain due to their high calorie and healthy fat content ###")
                with col1:
                    st.image(r"./eggs.png", width=230)
                    st.markdown("### Eggs can be a beneficial part of a diet for gaining weight due to their high protein content, healthy fats, and calorie density ###")
            elif st.session_state.goal == "lose":
                with col1:
                    st.image(r"./paneer.png", width=400)
                    st.markdown("### Paneer provides good fats, is high in protein, low in carbohydrates, and prevents our systems from storing as much fat since it contains short-chain fatty acids ###")
                with col1:   
                    st.image("./salad.png")
                    st.markdown("### Salads are beneficial for weight loss primarily because they are low in calories and high in fiber ###")
        else:
            st.warning("Please make a choice on the 'Choice' page first.")

if __name__ == "__main__":
    main()

conn.close()
