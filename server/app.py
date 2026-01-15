# server/app.py
from flask import Flask, session, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin

# ---- Database setup ----
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)

# ---- App factory ----
def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecretkey'

    # Override config if passed (for tests)
    if config:
        app.config.update(config)

    db.init_app(app)
    api = Api(app)

    # ---- Resources ----
    class Login(Resource):
        def post(self):
            username = request.get_json().get('username')
            user = User.query.filter_by(username=username).first()
            if user:
                session['user_id'] = user.id
                return {'logged_in': True, 'user': user.username}, 200
            return {'logged_in': False}, 401

    class Logout(Resource):
        def delete(self):
            session.pop('user_id', None)
            return {}, 204

    class CheckSession(Resource):
        def get(self):
            user_id = session.get('user_id')
            if user_id:
                user = db.session.get(User, user_id)  # Updated for SQLAlchemy 2.0+
                return {'logged_in': True, 'user': user.username}, 200
            return {'logged_in': False}, 401

    api.add_resource(Login, '/login')
    api.add_resource(Logout, '/logout')
    api.add_resource(CheckSession, '/check_session')

    return app


# ---- Run server ----
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)
