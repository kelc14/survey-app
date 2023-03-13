from flask import Flask, render_template, request, redirect, url_for, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey


app = Flask(__name__)
app.config['SECRET_KEY'] = "Survey-123"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS']= False


responses = []


@app.route('/')
def home_pg():
    title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    return render_template('home.html', title=title, instructions=instructions)

@app.route('/question/<num>')
def display_question(num):
    question_num = int(num)
    if len(responses) == question_num and question_num < len(satisfaction_survey.questions):
        route_name = f'/answer/{question_num}'
        question = satisfaction_survey.questions[question_num].question
        choices = satisfaction_survey.questions[question_num].choices
        return render_template('question.html', question=question, route_name=route_name, choices=choices, num=question_num)
    elif question_num != len(satisfaction_survey.questions):
        correct_num = len(responses)
        flash("Access Denied. Invalid Question Number", 'error')
        return redirect(url_for('display_question', num=correct_num))
    else:
        return redirect('/thank-you')

@app.route('/answer/<num>', methods=["POST"])
def record_ans(num):
    answer = request.form['customer_answer']
    responses.append(answer)
    next_num = int(num) + 1
    if next_num >= len(satisfaction_survey.questions):
        return redirect('/thank-you')
    else: 
        return redirect(url_for('display_question', num=next_num))
    

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')