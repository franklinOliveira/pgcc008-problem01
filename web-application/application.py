import sys
sys.path.append('resources/')
from controller import Controller

from flask import Flask, render_template, request

app = Flask(__name__)

controller = Controller()

@app.route('/')
def index():
    global controller
    return render_template('index.html', min = controller.getTempFormatted('MIN')
    , max = controller.getTempFormatted('MAX'))

@app.route('/', methods=['POST'])
def rangeChange():
    global controller
    action = request.form['range_change_button']
    if action == "min_up":
        controller.changeMinTemp(True)
    elif action == "min_down":
        controller.changeMinTemp(False)
    elif action == "max_up":
        controller.changeMaxTemp(True)
    elif action == "max_down":
        controller.changeMaxTemp(False)
    return render_template('index.html', min = controller.getTempFormatted('MIN')
    , max = controller.getTempFormatted('MAX'))

if __name__ == '__main__':
    app.run('localhost', 5000 ,use_reloader=True, use_debugger=True, use_evalex=True, debug=True)
