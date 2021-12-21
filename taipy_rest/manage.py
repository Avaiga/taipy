import click
from flask.cli import with_appcontext


@click.command("init")
@with_appcontext
def init():
    """Create a new admin user"""
    from taipy_rest.extensions import db
    from taipy_rest.models import User

    click.echo("create user")
    user = User(
        username="taipy.dev",
        email="taipy.dev@avaiga.com",
        password="taipy",
        active=True,
    )
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")
