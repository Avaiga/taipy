from .app import create_app

app = create_app()


def run():
    return app.run(debug=False)
