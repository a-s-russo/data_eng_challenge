import streamlit as st
import datetime
import time
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import pandas as pd
import textwrap
import inspect
from pytz import timezone

# Database setup
DATABASE_URL = "sqlite:///submissions.db"
Base = declarative_base()

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    function_code = Column(Text, nullable=False)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit app setup
st.title("Coding Challenge #1")

# Challenge description
c1, c2 = st.columns(2)
with c1:
    st.write("""
    Welcome to the inaugural ABS Data Engineers coding challenge! We're kicking things off with the Prisoner's Dilemma Game, where your strategic thinking is pitted against your colleagues in a classic scenario of cooperation and betrayal.""")
    st.markdown("[Prisoner's Dilemma on Wikipedia](https://en.wikipedia.org/wiki/Prisoner's_dilemma)")
with c2:
    st.image('two_prisoners.webp', width=300)

st.subheader("The Game Rules")
st.write("""
1. Objective: Each contestant will submit a function that decides whether to 'Cooperate' or 'Defect' based on the history of decisions in previous rounds.
2. Rounds: Each matchup consists of 50 rounds where contestants will be paired against each other.
3. Payoff Matrix:
    - Both Cooperate: 2 points each
    - One Cooperates, One Defects: Defector gets 3 points, Cooperator gets 0 points
    - Both Defect: 1 point each
4. Mystery Entrants:
    - Three mystery contestants have been added to the roster. Can you deduce their strategy?""")

st.subheader("Function Requirements")
st.write("""Your function should take a single parameter: a pandas DataFrame containing the history of decisions made by you and your opponent.

The DataFrame history will have the following columns:

- Round: The round number (starting from 1)
- Opponent_Decision: The opponent's decision in that round ('Cooperate' or 'Defect')
- My_Decision: Your decision in that round ('Cooperate' or 'Defect')
Your function should return either 'Cooperate' or 'Defect'.""")
st.subheader("Submission Template")
st.write("Below is a template you can use to create your function. Replace the placeholder logic with your strategy.")

code = """def my_strategy(history):
    # Example strategy: always cooperate
    if not history.empty:
        # Implement your strategy based on the history DataFrame
        pass
    return 'Cooperate'"""
st.code(code, language='python')

st.write("""Your task is to write a Python function that meets the specified requirements. 
The challenge submission will close on Thursday, 11/07 at 11:59 PM EST. The game will be run and broadcast on Teams on Friday, 12/07 at 3 PM EST. Good luck!
""")

# Countdown timer
aest = timezone('Australia/Sydney')
submission_close_date = aest.localize(datetime.datetime(2024, 7, 11, 23, 59, 59))
current_time = datetime.datetime.now(aest)
remaining_time = submission_close_date - current_time

st.sidebar.title("ABS Data Eng")
st.sidebar.header("Coding Challenge #1")
if remaining_time.total_seconds() > 0:
    st.sidebar.write(f"Submissions close in {remaining_time.days} days, {remaining_time.seconds // 3600} hours and "
                     f"{(remaining_time.seconds // 60) % 60} minutes.")
else:
    st.sidebar.write("Submissions Closed")

# Submission form
placeholder1 = """def nice_prisoner(history):
  return 'Cooperate'"""
if remaining_time.total_seconds() > 0:
    st.subheader("Submit your code")
    name = st.text_input("Name")
    function_code = st.text_area("Function Code (Paste your Python code here)", placeholder=placeholder1)

    if st.button("Submit"):
        if name and function_code:
            new_submission = Submission(name=name, function_code=function_code)
            session.add(new_submission)
            session.commit()
            st.success("Submission successful!")
        else:
            st.error("Please provide both name and function code.")
else:
    st.header("Submissions are now closed.")

# Display current entrants
st.sidebar.divider()
st.sidebar.header("Current Entrants")
entrants = session.query(Submission).all()

st.sidebar.write("### Entrants List")
for entrant in entrants:
    st.sidebar.write(f"- {entrant.name}")

st.sidebar.divider()
st.sidebar.header("Contact")

st.sidebar.write("Jono Sheahan")

# Admin section
st.sidebar.divider()
st.sidebar.header("Admin")
admin_password = st.sidebar.text_input("Password", type="password")

if admin_password == "charmander":  # Replace with a secure password management system in a real application
    
    # Show database entries
    st.sidebar.subheader("Database Entries")
    entries = session.query(Submission).all()
    for entry in entries:
        st.sidebar.write(f"ID: {entry.id}, Name: {entry.name}")
        st.sidebar.code(entry.function_code, language='python')
        
        # Delete entry button
        if st.sidebar.button(f"Delete {entry.name}", key=f"delete_{entry.id}"):
            session.delete(entry)
            session.commit()
            st.sidebar.success(f"Deleted entry {entry.name}")
            st.rerun()
    
    # Reset database button
    if st.sidebar.button("Reset Database"):
        session.query(Submission).delete()
        session.commit()
        st.sidebar.success("Database reset successfully")
        st.rerun()


# Test function
def test_submitted_function(func_code):
    local_vars = {}
    exec(textwrap.dedent(func_code), {}, local_vars)
    functions = {name: obj for name, obj in local_vars.items() if inspect.isfunction(obj)}
    if functions:
        func_name, test_func = next(iter(functions.items()))
        try:
            # Create a sample DataFrame
            data = {
                'Round': [1, 2, 3],
                'Opponent_Decision': ['Cooperate', 'Defect', 'Cooperate'],
                'My_Decision': ['Cooperate', 'Cooperate', 'Defect']
            }
            df = pd.DataFrame(data)
            
            # Run the function and check output
            result = test_func(df)
            if result in ['Defect', 'Cooperate']:
                return f"Function '{func_name}' passed all tests!"
            else:
                return f"Function '{func_name}' did not return 'Defect' or 'Cooperate'."
        except Exception as e:
            return f"Test case failed with function '{func_name}': {e}"
    else:
        return "No function found in the provided code."

# Test the submitted function
placeholder2 = """def nasty_prisoner(history):
  return 'Defect'"""
st.subheader("Optional: Test Your Function")
test_code = st.text_area("Paste the function code you want to test", placeholder=placeholder2)
if st.button("Run Tests"):
    result = test_submitted_function(test_code)
    st.write(result)
