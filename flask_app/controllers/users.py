from flask import Flask, render_template, session, redirect, request, flash
from flask_app import app
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['POST'])
def register():
    if not User.validate_register(request.form):
        return redirect('/')
    data ={ 
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password'])
    }
    id = User.save(data)
    session['user_id'] = id
    return redirect('/recipes')


@app.route('/login',methods=['POST'])
def login():
    user = User.get_by_email(request.form)
    # because we need to redirect to our root when either the email or 
    # password is invalid (doesn't exist in db)
    # we write the if statement here with the flash messages in our controller
    # rather than in our model but can be either or
    if not user:
        flash("Invalid Credentials","login")
        return redirect('/')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid Credentials","login")
        return redirect('/')
    
    # create a session with the newly logged in id.
    # this will be accessed by the /dashboard
    # in order to retrieve user information by that id
    session['user_id'] = user.id
    return redirect('/recipes')


@app.route('/logout')
def logout():
    #simple clear of all cookie sessions and redirect to root
    session.clear()
    return redirect('/')