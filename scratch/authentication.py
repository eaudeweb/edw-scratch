from flask import (
    redirect, url_for, request, render_template, current_app, Blueprint,
)
from flask.ext.login import (
    LoginManager, login_user, UserMixin, current_user, logout_user,
)


auth = Blueprint('auth', __name__)

login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def __unicode__(self):
        return self.id


@login_manager.user_loader
def load_user(userid):
    return userid and User(userid)


def login():
    username, password = (
        current_app.config['USERNAME'], current_app.config['PASSWORD']
    )
    if request.method == 'POST':
        if (
            request.form.get('username') == username and
            request.form.get('password') == password
        ):
            user = load_user(username)
            login_user(user, remember=True)
            return redirect(request.args.get('next') or url_for('.tenders'))
        else:
            return render_template('login.html', error=True)

    return render_template('login.html', error=False)


def logout():
    logout_user()
    return redirect(url_for('.tenders'))


@auth.before_app_request
def check_login():
    if 'login' in request.url or 'logout' in request.url:
        return None

    if current_user.is_authenticated():
        return None

    return redirect(url_for('.login', next=request.url))
