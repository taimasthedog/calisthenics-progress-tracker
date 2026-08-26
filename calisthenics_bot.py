import streamlit as st
import datetime
from supabase import create_client, Client
import pandas as pd
import matplotlib.pyplot as plt


# Supabase Connection
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
supabase = init_connection()

# Title
st.title("Progress Tracker")

# Password
user_password = st.text_input("Enter Password to Unlock", type="password")
if user_password != st.secrets["APP_PASSWORD"]:
    st.warning("Please enter the correct password to access the tracker.")
    st.stop()

# Button for choosing the exercise type
exercise_type = st.selectbox("Exercise",
                             ["Handstand Push-ups",
                              "Pull-ups",
                              "Muscle-ups",
                              "Dips"])

# Date button
workout_date = st.date_input("Date", datetime.date.today())

# Start and Finish time buttons
col1, col2 = st.columns(2)
start_time = col1.time_input("Start Time")
finish_time = col2.time_input("Finish Time")

# Reps button
reps_text = st.text_input("Reps (comma separated)", "10, 6, 4, 5, 5, 5, 5, 5, 4, 3")

# Processes the Data, Saves, and Makes Conclusions
if st.button("Log Workout"):
    try:
        start_dt = datetime.datetime.combine(workout_date, start_time)
        finish_dt = datetime.datetime.combine(workout_date, finish_time)
        duration = (finish_dt - start_dt).total_seconds() / 60

        rep_list = [int(x.strip()) for x in reps_text.split(',')]
        total_reps = sum(rep_list)
        density = total_reps / duration
        min_value = min(rep_list)
        max_value = max(rep_list)
        sets = len(rep_list)

        # Insert the data into Supabase
        supabase.table("workouts").insert({
            "date": workout_date.strftime("%Y-%m-%d"),
            "exercise": exercise_type,
            "duration": duration,
            "total_reps": total_reps,
            "density": density,
            "reps_array": reps_text,
            "min": min_value,
            "max": max_value,
            "sets": sets
        }).execute()

        st.success(f"Saved {total_reps} reps of {exercise_type} to Supabase!")

    except Exception as e:
        st.error("Error processing reps. Ensure they are comma-separated numbers.")

# Displays the database
st.divider()
st.title("Workout History")

# Read from Supabase (fetching all rows and ordering by date)
response = supabase.table("workouts").select("*").order("date", desc=True).execute()
df = pd.DataFrame(response.data)

# Hide the database ID column for a cleaner UI
if not df.empty:
    st.dataframe(df.drop(columns=['id']), use_container_width=True)
else:
    st.info("No workouts logged yet.")


# SUMMARY STATISTICS
st.divider()
st.title("Summary Statistics")

# Button for showing which exercise to choose
exercise_statistics = st.selectbox("Choose the exercise to show statistics",
                             ["Handstand Push-ups",
                              "Pull-ups",
                              "Muscle-ups",
                              "Dips"], key=1)

# Quick Summary
st.subheader(f"Quick Summary for {exercise_statistics}")
minimum = df['min'].min()
maximum = df['max'].max()
average = sum(df['total_reps']) / sum(df['sets'])
st.markdown(f"Minimum: {minimum}")
st.markdown(f"Maximum: {maximum}")
st.markdown(f"Average: {average}")


# Is my density growing for the exercise?
st.subheader(f"Is my endurance growing for {exercise_statistics}?")
st.write("Endurance = Total reps / Duration")

try:
    df = df.sort_values('date', ascending=True)
    fig, ax = plt.subplots()
    ax.plot(df['date'], df.loc[df['exercise'] == exercise_statistics, 'density'], marker='o')
    st.pyplot(fig)
except Exception as e:
    st.error("No data to process.")

