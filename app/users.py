from .all.forms import *
from .all.decorators import *

bluPrint = Blueprint('users', __name__, url_prefix='/')


@bluPrint.route("register", methods=['GET', 'POST'])
@is_anonymous
def register():
    form = RegisterForm()
    message = session.pop("message", None)
    if request.method == "GET":
        return render_template("register.html", **locals())
    elif request.method == "POST":
        post = request.form
        errors = form.validate(**post)
        if post['pwd'] and post['cpwd'] and post['pwd'] != post['cpwd']:
            errors.append("Passwords do not match!")
        if len(errors) > 0:
            return render_template("register.html", **locals())
        user = User().get(username=post['username'])
        if not user.exists():
            token = gener_token()
            ip_info = get_ip_info(request.remote_addr)
            User().create(
                username=escape(post['username'], quote=True),
                gender=escape(post['gender'], quote=True),
                firstname=escape(post['firstname'].capitalize(), quote=True),
                lastname=escape(post['lastname'].upper(), quote=True),
                birthdate=escape(post['birthdate'], quote=True),
                age=calculate_age(escape(post['birthdate'], quote=True)),
                email=escape(post['email'], quote=True),
                password=hash_pw(post['pwd']),
                latitude=ip_info['latitude'],
                longitude=ip_info['longitude'],
                city=ip_info['city'],
                token=token
            )
            msg = "Hey {}, Welcome to Matcha dating site !\n\n Please confirm your registration by clicking the link: http://127.0.0.1:8080/confirm?token={}\n\nSee you SOON!!!\n\n\nMatcha Team".format(post['username'], token)
            send_mail(post['email'], "Matcha Confirmation", msg)
            session['message'] =  "You are registered ! A confirmation email has just been sent !"
        else:
            errors.append("Username already exist, please choose another one")
            return render_template("register.html", **locals())
        return redirect(url_for('users.login'))


@bluPrint.route("login", methods=['GET', 'POST'])
@is_anonymous
def login():
    form = LoginForm()
    message = session.pop("message", None)
    if request.method == "GET":
        return render_template("login.html", **locals())
    elif request.method == "POST":
        post = request.form
        errors = form.validate(**post)
        if len(errors) > 0:
            return render_template("login.html", **locals())
        user = User().get(username=post['username'])
        if user.exists():
            if user.password == hash_pw(post['password']):
                if user.confirm == 0:
                    errors.append("Please confirm your account via email before loggin in!")
                else:
                    if not user.latitude or not user.longitude or not user.city:
                        ip_info = get_ip_info(request.remote_addr)
                        user.update('id', user.id, latitude=ip_info['latitude'], longitude=ip_info['longitude'], city=ip_info['city'], last_connection=datetime.datetime.now())
                    else:
                        user.update('id', user.id, last_connection=datetime.datetime.now(), is_connected=1)
                    session['user'] = user.__dict__
                    session['logged'] = True
                    session['message'] = "You are well connected, well respected and well protected!"
                    return redirect(url_for('home.home'))
            else:
                errors.append("Password is wrong!")
        else:
            errors.append("Username is not found, please register before loggin in")
        return render_template("login.html", **locals())


@bluPrint.route("confirm")
@is_anonymous
def confirm():
    if "token" in request.args.keys():
        token = request.args['token']
        user = User().get(token=token)
        if user.exists():
            User().update("token", token, confirm=1)
            session['message'] = "Registration has been confirmed!"
        else:
            session['message'] = "Token is unknown!"
    return redirect(url_for('users.login'))


@bluPrint.route("reset", methods=['GET', 'POST'])
@is_anonymous
def reset():
    form = ResetForm()
    message = session.pop("message", None)
    if request.method == "GET":
        return render_template("reset.html", **locals())
    elif request.method == "POST":
        post = request.form
        errors = form.validate(**post)
        if len(errors) > 0:
            return render_template("reset.html", **locals())
        user = User().get(email=post['email'])
        if user.exists():
            token = gener_token()
            User().update("email", post['email'], token=token)
            msg = "Hello {} !\n\n Click the link to reset your password : http://127.0.0.1:8080/reset-done?token={}\n\nNow get back to the Love Game!!!\n\n\nMatcha Team".format(
                user.username, token)
            send_mail(escape(post['email']), "Matcha Reset Password", msg)
            session['message'] = "The link has been sent, Please check your email before loggin in!"
            return redirect(url_for("users.login"))
        else:
            errors.append("Email address is not on the database, please register!")
        return render_template("reset.html", **locals())


@bluPrint.route("reset-done", methods=['GET', 'POST'])
@is_anonymous
def reset_done():
    form = NewPasswordForm()
    message = session.pop("message", None)
    token = request.args.get('token', None, str)
    if request.method == "GET":
        if not token:
            return redirect(url_for("users.login"))
        session['token'] = token
        if not User().get(token=token).exists():
            session['message'] = "Token is unknown!"
            return redirect(url_for("users.login"))
        return render_template("reset-done.html", **locals())
    elif request.method == "POST":
        post = request.form
        errors = form.validate(**post)
        if post['pwd'] and post['cpwd'] and post['pwd'] != post['cpwd']:
            errors.append("Passwords do not match")
        if len(errors) > 0:
            return render_template("reset-done.html", **locals())
        User().update('token', session['token'], password=hash_pw(post['pwd']), token="")
        del session['token']
        session['message'] = "Password has been reset!"
        return redirect(url_for("users.login"))


@bluPrint.route("logout")
@is_authenticated
def logout():
    session['logged'] = False
    User().update('id', session['user']['id'], is_connected=0)
    session.pop('user', None)
    session['message'] = "You are now disconnected!"
    return redirect(url_for('users.login'))
