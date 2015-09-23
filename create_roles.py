from app.models import Role
from app import db
role1 = Role(code="admin", name="Admin")
role2 = Role(code="company_admin", name="Company Admin")
role3 = Role(code="driver", name="Driver")
db.session.add(role1)
db.session.add(role2)
db.session.add(role3)
db.session.commit()