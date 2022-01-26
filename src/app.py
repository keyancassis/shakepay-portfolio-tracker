from flask import Flask, render_template
from waitress import serve
from tracker import calculate_balances

webapp = Flask(__name__)
APP_PORT = 5000


@webapp.route("/", methods=['GET'])
def serve_page():
    # get portfolio balances then render and serve template
    balances = calculate_balances()
    return render_template('index.html', data=balances)


if __name__ == '__main__':
    print(f'Serving app at http://localhost:{APP_PORT}')
    serve(webapp, host="0.0.0.0", port=APP_PORT)
