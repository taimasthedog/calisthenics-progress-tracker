import streamlit as st
import datetime
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

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
                              "Dips",
                              "Pike push-ups",
                              "Australian pull-ups",
                              "Push-ups",
                              "Negative Pull-ups"])

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

 # Calculate average rest days
df['date'] = pd.to_datetime(df['date'])
unique_dates = df['date'].drop_duplicates().sort_values()
rest_days = unique_dates.diff().dt.days
average_rest = rest_days.dropna().mean()

if pd.isna(average_rest):
    display_rest = "Need more data"
else:
    display_rest = f"{round(average_rest, 1)} days"

st.metric("Average resting time between sessions", display_rest)


# SUMMARY STATISTICS
st.divider()
st.title("Summary Statistics")

# Button for showing which exercise to choose
exercise_statistics = st.selectbox("Choose the exercise to show statistics",
                             ["Handstand Push-ups",
                              "Pull-ups",
                              "Muscle-ups",
                              "Dips",
                              "Pike push-ups",
                              "Australian pull-ups",
                              "Push-ups",
                              "Negative Pull-ups"], key=1)

# Make a filtered copy of the df
filtered_df = df[df['exercise'] == exercise_statistics].copy()
filtered_df['mean'] = filtered_df['total_reps'] / filtered_df['sets']

# Quick Summary
if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)

    minimum = filtered_df['min'].min()
    maximum = filtered_df['max'].max()
    total_reps_all = filtered_df['total_reps'].sum()
    total_sets_all = filtered_df['sets'].sum()
    average = avg_reps = round(total_reps_all / total_sets_all, 1) if total_sets_all > 0 else 0
    total_sessions = filtered_df['date'].nunique()

    col1.metric("Your minimum:", int(minimum))
    col2.metric("Your maximum:", int(maximum))
    col3.metric("Your average:", average)
    col4.metric("Total sessions done:", total_sessions)

    # Visualizations
    filtered_df = filtered_df.sort_values('date', ascending=True)

    st.divider()
    fig1 = px.line(filtered_df,
                   x='date',
                   y='mean',
                   markers=True,
                   title="Average Reps Over Time")
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()
    fig1 = px.line(filtered_df,
                   x='date',
                   y='density',
                   markers=True,
                   title="Endurance Over Time")
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()
    fig2 = px.line(filtered_df,
                   x='date',
                   y='total_reps',
                   markers=True,
                   title="Total Reps per Session Over Time")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    fig3 = px.line(filtered_df,
                   x='date',
                   y='duration',
                   markers=True,
                   title="Duration of the Sessions Over Time")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info(f"No data available for {exercise_statistics} yet.")


