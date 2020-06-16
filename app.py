from flask import Flask
#from flask_restplus import Api

app = Flask(__name__)
# api = Api(app, version='1.0', title='API title', description='A simple API')

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/route')
def hello_route():
    return 'Hello Route!'




if __name__ == '__main__':
    app.run()
