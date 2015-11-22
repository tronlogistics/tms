from app import db
from app.models import User, Role

user1 = User.query.filter_by(email="johnny.lopez617@gmail.com").first()
role = Role.query.filter_by(code="admin").first()
user1.roles.append(role)
user2 = User.query.filter_by(email="john@tronlogistics.com").first()
user2.roles.append(role)
db.session.add(user1)
db.session.add(user2)
db.session.commit()
