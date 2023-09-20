from flask import Flask, render_template, request, redirect, url_for
import os
from apikey import mykey
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

app = Flask(__name__, static_url_path='/static')

# Default values for level and tense
level = None
tense = None

# home page
@app.route('/')
def home():
    return render_template('home.html')

#set profficiency level
@app.route('/set_level/<chosen_level>')
def set_level(chosen_level):
    global level
    level = chosen_level
    return redirect(url_for('home'))

#set tense to study
@app.route('/set_tense/<chosen_tense>')
def set_tense(chosen_tense):
    global tense
    tense = chosen_tense
    return redirect(url_for('level_select'))

# level/tense select page
@app.route('/level_select')
def level_select():
    return render_template('level_select.html')

# 
@app.route('/final_page')
def final_page():

    os.environ['OPENAI_API_KEY'] = mykey

    quiz_template = PromptTemplate(
        input_variables = ['level', 'tense'], 
        template='You are a Spanish teacher, teaching spanish to native English speakers. Generate an {level} 10 question multiple choice quiz in English about the {tense} tense using verb conjugation, then generate an answer key titled Key: with only the correct letter on each sequential lines, meaning there should be 10 sequential lines with only a the correct letter on each line. '
    )

    # calling the llm and giving it our template to generate a response
    llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo")
    quiz_chain = LLMChain(llm=llm, prompt=quiz_template, output_key='quiz')
    response = quiz_chain.run(level=level, tense=tense)

    # splitting the quiz and ans. key with key delimiter
    delimiter = "Key:"
    parts = response.split(delimiter, 1)  # The second argument (1) limits the split to one occurrence
    if len(parts) > 1:
        quiz, key = parts
        print("Quiz:", quiz)
    else:
        print("Delimiter not found in the string.")


    # Split the input string into a list of lines
    lines = key.split('\n')

    # Remove any empty lines from the result (optional)
    key_list = [line.strip() for line in lines if line.strip()]

    output = f"{quiz}"

    keystr = ", ".join(key_list)

    fin_key = "Key: "+ keystr

    return render_template('final_page.html', output=output, key=fin_key)



if __name__ == '__main__':
    app.run(debug=True)
