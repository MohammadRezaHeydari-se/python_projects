from flask import Flask, render_template, request, make_response, jsonify
from .api import api # Det här kommer vara våran API blueprint
from .views import register_views

app = Flask(__name__)
app.register_blueprint(api)
register_views(app)

def create_app():
    from .views import register_views
    from flask import Flask

    app = Flask(__name__)
    register_views(app)
    return app

@app.get("/")
def health():
    return jsonify({"ok": True, "service": "gutendach-backend"})



if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)