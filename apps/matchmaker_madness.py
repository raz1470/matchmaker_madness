import streamlit as st
import pandas as pd

# Title of the app
st.title("Matchmaker Madness")
st.subheader("How well do you really know your team?!")
st.write("Get ready for a fun-filled guessing game! Can you and your teammates work together to figure out who gave which answer? It's time to see how well you really know your team!")

st.markdown("""
#### How the game works:
- A team lead needs to be nominated.
- The team lead needs to think of 5 questions and then they will run an anonymous survey to collect answers from the team:
    - It is important that only the team lead see's the answers!
    - Questions can be serious, funny or obscure - A mix of these 3 usually works well!
- The questions and answers can then be uploaded to this app.
- The team then need to work together and try and figure out who gave which answer:
    - The overall aim is to score a high as possible as a team.
    - If you give away what your answer was this ruins the game!
""")

st.markdown("""
#### File upload instructions:
To ensure your game runs smoothly, please format your CSV file as follows:

| Column Name | Description                                |
|-------------|--------------------------------------------|
| question    | The text of the question.                  |
| name        | The name of the person who gave the answer.|
| answer      | The answer provided by the person.         |
""")

# Initialize the total score in session state if it doesn't exist
if 'total_score' not in st.session_state:
    st.session_state['total_score'] = 0

# File uploader for the CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Shuffle the answers for randomness, keeping the original name-answer association
    shuffled_df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Grouping by questions and displaying the corresponding answers
    questions_grouped = df.groupby('question')

    for question, group in questions_grouped:
        with st.form(key=f'{question}_form'):
            st.write(f"### Question: {question}")
            
            # Create a dataframe for displaying the question's answers
            display_data = pd.DataFrame({
                'Answer': group['answer'].values,
                'Your Guess': ['' for _ in range(len(group))],
            })

            # Store guesses for this question
            guesses = {}

            for idx, (i, row) in enumerate(group.iterrows()):
                answer = row['answer']
                correct_name = row['name']
                
                guess = st.selectbox(f"Who gave this answer? (Answer: {answer})", df['name'].unique(), key=f'{question}_answer_{i}')
                guesses[f'{question}_answer_{i}'] = guess
                
                display_data.at[idx, 'Your Guess'] = guess

            submitted = st.form_submit_button(f"Submit Answers for Question: {question}")

            if submitted:
                correct_count = 0

                for idx, (i, row) in enumerate(group.iterrows()):
                    correct_name = row['name']
                    user_guess = guesses[f'{question}_answer_{i}']

                    if user_guess == correct_name:
                        display_data.at[idx, 'Result'] = '✔️ Correct'
                        correct_count += 1
                    else:
                        display_data.at[idx, 'Result'] = f'❌ Wrong (Correct: {correct_name})'

                # Update total score in session state
                st.session_state['total_score'] += correct_count

                # Display results for this question
                st.write(f"Results for Question: {question}")
                st.write(display_data)
                st.write(f"You got {correct_count} out of {len(group)} correct for this question!")

    # Display total score after all questions
    st.write(f"### Your Total Score So Far: {st.session_state['total_score']}")

else:
    st.write("Please upload a CSV file to start the game.")
