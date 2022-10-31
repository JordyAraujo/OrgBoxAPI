import os, base64

from flask import Flask
from flask_login import LoginManager

from .models.user import User
from .models import db

from .blueprints.auth import auth as auth_blueprint


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "secret-key-goes-here"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.request_loader
    def load_user_from_request(request):

        # first, try to login using the api_key url arg
        api_key = request.args.get('api_key')
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # next, try to login using Basic Auth
        api_key = request.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            try:
                api_key = base64.b64decode(api_key)
            except TypeError:
                pass
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # finally, return None if both methods did not login the user
        return None

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_blueprint)

    return app