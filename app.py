from flask import Flask

app = Flask(__name__)
app.config.from_object('config.Config')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug = True)