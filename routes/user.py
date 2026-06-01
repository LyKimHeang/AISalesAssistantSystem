from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect
)
from database import search_product, save_chat_history
from ai import get_ai_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['GET', 'POST'])
def home():

    ai_response    = None
    user_question  = None

    if request.method == 'POST':

        # 1. Get the question the customer typed
        user_question = request.form['product']

        # 2. Search the database for matching product
        product = search_product(user_question)

        # 3. Send question + product data to OpenAI and get a reply
        ai_response = get_ai_response(user_question, product)

        # 4. Save the conversation to chat_history table
        save_chat_history(user_question, ai_response, platform="website")

    return render_template(
        'index.html',
        ai_response=ai_response,
        user_question=user_question
    )


@user_bp.route('/dashboard')
def dashboard():

    if session.get('role') != 'buyer':
        return redirect('/login')

    return render_template('dashboard.html')
