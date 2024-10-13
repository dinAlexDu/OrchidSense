from app import db, app
from users import User

with app.app_context():
    db.create_all()

    admin_user = User(email="dinis.duarte@my.istec.pt")
    admin_user.set_password("TQZzvd37RV5ySfeGwjrU98")
    admin_user.is_admin = True


    db.session.add(admin_user)
    db.session.commit()


    print(User.query.all())
