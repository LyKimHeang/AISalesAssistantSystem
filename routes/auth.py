from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session
)

from database import (
    create_user,
    verify_user,
    get_user_by_email
)

auth_bp = Blueprint(
    'auth',
    __name__
)


@auth_bp.route('/register',
               methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        existing_user = get_user_by_email(
            email
        )

        if existing_user:

            return render_template(
                'register.html',
                message='Email already exists'
            )

        create_user(email, password)

        return redirect('/login')

    return render_template(
        'register.html'
    )
    

@auth_bp.route('/login',
               methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = verify_user(
            email,
            password
        )

        if not user:

            return render_template(
                'login.html',
                message='Invalid credentials'
            )

        session['user_id'] = user[0]
        session['email']   = user[1]
        session['role']    = user[3]

        if user[3] == 'seller':
            return redirect('/admin')

        return redirect('/dashboard')

    return render_template(
        'login.html'
    )


@auth_bp.route('/logout')
def logout():

    session.clear()

    return redirect('/')