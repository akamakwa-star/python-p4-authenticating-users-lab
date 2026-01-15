
from app import create_app
from models import db, User, Article

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.first():
        user = User(username="testuser")
        db.session.add(user)
        db.session.commit()

    if not Article.query.first():
        article = Article(
            author="testuser",
            title="Member Only Article",
            content="This is a member-only article.",
            preview="Preview text",
            minutes_to_read=5,
            is_member_only=True,
            user_id=User.query.first().id
        )
        db.session.add(article)
        db.session.commit()

    print("Database seeded with 1 user and 1 member-only article.")
