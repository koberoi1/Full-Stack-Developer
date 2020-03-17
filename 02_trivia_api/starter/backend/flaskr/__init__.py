import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in questions]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_catetogry():
      categories =  Category.query.all()
      res = {}
      for c in categories:
        res[c.id] = c.type
      return jsonify(res)

  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.


  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

  @app.route('/questions')
  def get_questions():

    categories = {}
    for category in Category.query.all():
        categories[category.id] = category.type

    questions = Question.query.all()
    current_questions = paginate_questions(request=request, questions=questions)


    return jsonify({
            'questions': current_questions ,
            'total_questions': len(questions),
            'categories': categories
        })
        #
    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  @app.route('/questions',methods = ['POST'])
  def post_question():
    body = request.get_json()
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_category = body.get('category')
    new_difficulty = body.get('difficulty')

    try:
      question = Question(question=new_question,answer=new_answer, category=new_category, difficulty=new_difficulty)
      question.insert()

      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      return abort(422)

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  @app.route('/search', methods=['POST'])
  def search():
    if request.data:
        body = request.get_json()
        search_term = body.get("searchTerm")
        questions = Question.query.filter(
                      Question.question.ilike(
                          '%' +
                          search_term +
                          '%')).all()
        current_questions = paginate_questions(questions=questions, request=request)

        if len(current_questions) > 0:
            return jsonify({
                  "success": True,
                  "questions": current_questions,
                  "total_questions": len(questions),
                  "current_category": None
                  })
        else:
            return abort(404)

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):

    if not category_id:
        return abort(422)
    questions = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_questions(questions=questions, request=request)

    return jsonify({
        'questions': current_questions,
        'total_questions': len(questions),
        'current_category': category_id
    })

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_question_to_play():
      try:
          body = request.get_json()

          if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

          category = body.get('quiz_category')
          previous_questions = body.get('previous_questions')

          if category['type'] == 'click':
              available_questions = Question.query.filter(
              Question.id.notin_((previous_questions))).all()
          else:
              available_questions = Question.query.filter_by(
              category=category['id']).filter(Question.id.notin_((previous_questions))).all()

          current_questions = paginate_questions(questions=available_questions, request=request)

          return jsonify({
            'success': True,
            'question': current_questions
        })
    except:
        abort(422)

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource not found"
      }), 404

  @app.errorhandler(422)
  def not_found(error):
      return jsonify({
      "success": False,
      "error": 422,
      "message": "The request was well-formed but was unable to be followed due to semantic errors"
      }), 422


  return app
