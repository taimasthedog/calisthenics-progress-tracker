# Calisthenics Progress Tracker

Simple, easy-to-use progress tracker written in python. Just fill out your data while training, it summarizes and visualizes your progress. Fully accessible and customizable for your needs.


# How to use it? 
## 1. Clone this repository and navigate into the project directory:

```
git clone https://github.com/taimasthedog/calisthenics-progress-tracker.git
cd calisthenics-progress-tracker
```

## 2. Install the required Python libraries using the 'requirements.txt':

```
pip install -r requirements.txt
```

## 3. Set Up the Database. 
This app uses Supabase for cloud data storage. You can use Google Sheets, Firebase (I haven't tried them).

   1) Create a new project in Supabase.
   2) Navigate to the SQL Editor in your Supabase dashboard.
   3) Run the following SQL command to create the required table:

```
CREATE TABLE workouts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    date TEXT,
    exercise TEXT,
    duration REAL,
    total_reps INTEGER,
    density REAL,
    reps_array TEXT,
    min INTEGER,
    max INTEGER,
    sets INTEGER
);
```

## 4. Configure Secure Environment Variables

1) Inside the project folder, create a hidden directory named '.streamlit'.
2) Inside that directory, create a file named 'secrets.toml'.
3) Add your Supabase credentials and a custom app password:
  
Inside the 'secrets.toml' copy-paste this and fill out your Supabase URL, key, and set your own password:

```
SUPABASE_URL = "https://your-project-url.supabase.co"
SUPABASE_KEY = "your-service-role-key"
APP_PASSWORD = "your_secret_password"
```

## 5. Run the Application

```
streamlit run your_app_filename.py
```

   
