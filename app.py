from flask import Flask, render_template, request, redirect, flash
from flask import session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey, surveys


app = Flask(__name__)
app.config['SECRET_KEY'] = "Survey-123"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS']= False

CURRENT_SURVEY_TYPE = 'current_survey'
USER_RESPONSES = 'responses'

@app.route('/')
def display_surveys():
    """ display all available surveys to the user. """
    return render_template('selection-page.html', surveys=surveys)


@app.route("/", methods=["POST"])
def pick_survey():
    """Select a survey. IF the user already completed the survey, redirects to thank you page"""

    survey_type = request.form['survey_type']

    if request.cookies.get(f"completed_{survey_type}"):
        return redirect('/completed')
    

    session[CURRENT_SURVEY_TYPE] = survey_type

    return redirect('/start')


@app.route('/start')
def show_instructions():
    """Display start screen for selected survey, including title and instructions."""
    survey_type=session[CURRENT_SURVEY_TYPE]
    survey = surveys[f'{survey_type}']
    session['title']=survey.title
    session['instructions']=survey.instructions

    return render_template("home.html")


@app.route("/start", methods=["POST"])
def start_survey():
    """Clear the session of user's previous responses."""

    session[USER_RESPONSES] = []


    return redirect("/questions/0")


@app.route('/questions/<int:ques_num>')
def display_question(ques_num):
    """ display correct question to the user """

    survey_type = session[CURRENT_SURVEY_TYPE]
    survey = surveys[f'{survey_type}']

    responses = session.get(USER_RESPONSES)

# if the user is trying to access a question before the survey began, return to home
    if (responses is None):
        flash('You have not yet chosen a survey to complete.')
        return redirect('/')
    
# if the user is trying to access a question after they have completed the survey, go to completed
    if (len(responses) == len(survey.questions)):
        return redirect('/completed')

# if the user is trying to access the incorrect question number, redirect to the correct question
    if (len(responses) != int(ques_num)):
        return redirect(f"{len(responses)}")
    
    question = survey.questions[int(ques_num)].question
    choices = survey.questions[int(ques_num)].choices
    return render_template('question.html', choices=choices, question_index=int(ques_num), question=question )


@app.route('/answer', methods=["POST"])
def record_ans():
    """Record the users responses along with the question in session. Then either direct to thank you page (if survey completed), otherwise direct to next question"""
    survey_code = session[CURRENT_SURVEY_TYPE]
    survey = surveys[survey_code]
    customer_answer = request.form['customer_answer']


    responses = session[USER_RESPONSES]
    question = survey.questions[len(responses)].question

    responses.append({f"{question}": customer_answer}) 

    session[USER_RESPONSES] = responses
    

    if (len(responses) == len(survey.questions)):
        return redirect("/thank-you")

    else:
        return redirect(f"/questions/{len(responses)}")
    
    
@app.route('/thank-you')
def thank_you():
    """display the thank you page, as well as user responses to the survey.  Also set the survey cookie as completed so that users cannot retake the survey until it expires (24 hrs)"""
    responses = session[USER_RESPONSES]
    survey_type = session[CURRENT_SURVEY_TYPE]

    html = render_template('thank_you.html', responses=responses)
    html_resp = make_response(html)
    html_resp.set_cookie(f"completed_{survey_type}", "True", max_age=86400)

    return html_resp

@app.route('/completed')
def already_completed():
    """display a page letting the user know that they have already completed this survey."""
    return render_template("already_completed.html")


# 