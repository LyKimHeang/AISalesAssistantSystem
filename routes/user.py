from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect
)
from database import search_product

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET', 'POST'])
def home():

    result = None
    message = None

    if request.method == 'POST':

        product = request.form['product']

        result = search_product(product)

        if result:
            message = "✅ Product found"
        else:
            message = "❌ Product not found"

    return render_template(
        'index.html',
        result=result,
        message=message
    )
    
@user_bp.route('/dashboard')
def dashboard():

    if session.get('role') != 'buyer':
        return redirect('/login')

    return render_template('dashboard.html')