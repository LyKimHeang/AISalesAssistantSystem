from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect
)
from database import (
    search_product,
    save_chat_history,
    get_all_chat_history,
    get_all_products
)
from ai import get_ai_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['GET', 'POST'])
def home():

    ai_response   = None
    user_question = None

    if request.method == 'POST':
        user_question = request.form['product']
        product       = search_product(user_question)
        ai_response   = get_ai_response(user_question, product)
        save_chat_history(user_question, ai_response, platform="website")

    return render_template(
        'index.html',
        ai_response=ai_response,
        user_question=user_question
    )


@user_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if session.get('role') not in ('buyer', 'seller'):
        return redirect('/login')

    ai_response   = None
    user_question = None

    if request.method == 'POST':
        user_question = request.form['product']
        product       = search_product(user_question)
        ai_response   = get_ai_response(user_question, product)
        save_chat_history(user_question, ai_response, platform="website")

    chat_history = get_all_chat_history()
    products     = get_all_products()

    return render_template(
        'dashboard.html',
        ai_response=ai_response,
        user_question=user_question,
        chat_history=chat_history,
        products=products
    )