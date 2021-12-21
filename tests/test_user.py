from flask import url_for

from taipy_rest.extensions import pwd_context
from taipy_rest.models import User


def test_get_user(client, db, user):
    # test 404
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.get(user_url)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    # test get_user
    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.get(user_url)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["active"] == user.active


def test_put_user(client, db, user):
    # test 404
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.put(user_url)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    data = {"username": "updated", "password": "new_password"}

    user_url = url_for('api.user_by_id', user_id=user.id)
    # test update user
    rep = client.put(user_url, json=data)
    assert rep.status_code == 200

    data = rep.get_json()["user"]
    assert data["username"] == "updated"
    assert data["email"] == user.email
    assert data["active"] == user.active

    db.session.refresh(user)
    assert pwd_context.verify("new_password", user.password)


def test_delete_user(client, db, user):
    # test 404
    user_url = url_for('api.user_by_id', user_id="100000")
    rep = client.delete(user_url)
    assert rep.status_code == 404

    db.session.add(user)
    db.session.commit()

    # test get_user

    user_url = url_for('api.user_by_id', user_id=user.id)
    rep = client.delete(user_url)
    assert rep.status_code == 200
    assert db.session.query(User).filter_by(id=user.id).first() is None


def test_create_user(client, db):
    # test bad data
    users_url = url_for('api.users')
    data = {"username": "created"}
    rep = client.post(users_url, json=data)
    assert rep.status_code == 400

    data["password"] = "admin"
    data["email"] = "create@mail.com"

    rep = client.post(users_url, json=data)
    assert rep.status_code == 201

    data = rep.get_json()
    user = db.session.query(User).filter_by(id=data["user"]["id"]).first()

    assert user.username == "created"
    assert user.email == "create@mail.com"


def test_get_all_user(client, db, user_factory):
    users_url = url_for('api.users')
    users = user_factory.create_batch(30)

    db.session.add_all(users)
    db.session.commit()

    rep = client.get(users_url)
    assert rep.status_code == 200

    results = rep.get_json()
    for user in users:
        assert any(u["id"] == user.id for u in results["results"])
