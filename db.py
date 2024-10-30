from data import db_session
from data.users import Users
import json

db_session.global_init("database/eljur.db")
db_sess = db_session.create_session()


def add_user(user_id, login, password):
    delete_user(user_id)
    user = Users()
    user.user_id = user_id
    user.login = login
    user.password = password
    db_sess.add(user)
    db_sess.commit()

    with open("database/time.json", "r") as f:
        data = json.load(f)
    if str(user_id) not in data:
        set_time(user_id, 600)


def set_time(user_id, time):
    with open("database/time.json", "r") as f:
        d = json.load(f)
    d[str(user_id)] = time
    with open("database/time.json", "w") as f:
        json.dump(d, f)


def delete_user(user_id):
    data = db_sess.query(Users).filter(Users.user_id == user_id).first()
    if data:
        db_sess.delete(data)
    with open("database/time.json", 'r') as f:
        d = json.load(f)
    if str(user_id) in d:
        del d[str(user_id)]
    with open("database/time.json", 'w') as f:
        json.dump(d, f)


def get_time(user_id):
    with open("database/time.json", "r") as f:
        d = json.load(f)
        return d[str(user_id)]


def get_authorization(user_id):
    data = db_sess.query(Users).filter(Users.user_id == user_id).first()
    return data.login, data.password


def get_users():
    data = db_sess.query(Users).all()
    user_ids = [i.user_id for i in data]
    return user_ids
