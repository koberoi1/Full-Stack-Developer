import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#  including pagination (every 10 questions).
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

 #Set up CORS. Allow '*' for origins.
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  @app.route('/categories')
  def get_catetogry():
      categories =  Category.query.all()
      response = {}
      for c in categories:
        response[c.id] = c.type
    # abort 404 if no categories found
      if (len(response) == 0):
        abort(404)

      return jsonify({
        'success': True,
        'categories': response
})

#  endpoint to handle GET requests for questions,
#  This endpoint should return a list of questions,
#  number of total questions, current category, categories.

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

# endpoint to DELETE question using a question ID.
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

  # POST a new question,
  # which will require the question and answer text,
  # category, and difficulty score.

  @app.route('/questions',methods = ['POST'])
  def post_question():

    if request.data:
        # load the request body
        body = request.get_json()
        # load data from body
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        if (new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None):
            abort(422)


    # ensure all fields have data
    else:
        abort(422)

    try:
        # create and insert new question
        question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty, category=new_category)
        question.insert()

        # get all questions and paginate
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        # return data to view
        return jsonify({
            'success': True,
            'created': question.id,
            'question_created': question.question,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })

    except:
    # abort unprocessable if exception
        abort(422)

# POST endpoint to get questions based on a search term.
# It should return any questions for whom the search term
# is a substring of the question.

  @app.route('/search', methods=['POST'])
  def search():
    if not request.data:
        return abort(422)

    body = request.get_json()
    search_term = body.get("searchTerm")

    try:
        questions = Question.query.filter(
                  Question.question.ilike(
                      '%' +
                      search_term +
                      '%')).all()
        current_questions = paginate_questions(questions=questions, request=request)

        return jsonify({
              "success": True,
              "questions": current_questions,
              "total_questions": len(questions),
              "current_category": None
              })

    except:
        abort(422)



  #Create a GET endpoint to get questions based on category.
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):

    if category_id:
        questions = Question.query.filter(Question.category == category_id).all()
        current_questions = paginate_questions(questions=questions, request=request)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': category_id
        })
    else:
        return abort(422)

  @app.route('/quizzes', methods=['POST'])
  def get_question_to_play():
      try:
          #{'previous_questions': [], 'quiz_category': {'type': 'Art', 'id': '2'}}
          body = request.get_json()

          if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

          category = body.get('quiz_category')
          previous_questions = body.get('previous_questions')

          if category['type'] == 'click':
              available_questions = Question.query.filter(
              Question.id.notin_(previous_questions)).first()
          else:
              available_questions = Question.query.filter_by(
              category=category['id']).filter(Question.id.notin_((previous_questions))).first()

        #Returns 1 new question everytime
          return jsonify({
            'success': True,
            'question': available_questions.format()
        })
      except:
          abort(422)

###########################
#Error Handlers
###########################
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
