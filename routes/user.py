from flask import Blueprint, render_template, request, session, redirect, jsonify
from database import search_product, save_chat_history, get_all_products
from ai import get_ai_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['GET', 'POST'])
def home():
    ai_response   = None
    user_question = None

    if request.method == 'POST':
        user_question = request.form['product']
        products      = get_all_products()
        ai_response   = get_ai_response(user_question, products)
        save_chat_history(user_question, ai_response, platform="website")

    return render_template('index.html',
        ai_response=ai_response,
        user_question=user_question
    )


# ── AJAX chat endpoint (floating widget on every page) ─────────────────────────
@user_bp.route('/chat', methods=['POST'])
def chat_api():
    data       = request.get_json() or {}
    question   = data.get('question', '').strip()
    history    = data.get('history', [])       # conversation so far
    session_id = data.get('session_id', None)  # ties messages into one session

    if not question:
        return jsonify({'response': 'Please type a question first.'})

    products    = get_all_products()
    ai_response = get_ai_response(question, products, history)
    save_chat_history(question, ai_response, platform="website", session_id=session_id)

    return jsonify({'response': ai_response})


@user_bp.route('/dashboard')
def dashboard():
    if session.get('role') not in ('buyer', 'seller'):
        return redirect('/login')
    return render_template('dashboard.html')