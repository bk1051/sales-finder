from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello world!"

@app.route('/<name>')
def hello_name(name):
	return "Hello, %s" % name

if __name__ == '__main__':
    app.run()