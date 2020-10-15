import sys
sys.path.append('resources/')
from controller import Controller
import time

from flask import Flask, render_template, request, redirect, Response

app = Flask(__name__)

controller = Controller()


@app.route('/')
def index():
    global controller
    controller.refreshData()

    return render_template('index.html', min = controller.getTempFormatted('MIN')
    , max = controller.getTempFormatted('MAX'), in_temp = controller.getTempFormatted('IN_TEMP')
    , in_hum = controller.getHumFormatted(), in_air_cond_state = controller.getAirCondState()
    , ex_temp = controller.getTempFormatted('EX_TEMP'))

@app.route('/rangeChange/', methods=['POST'])
def rangeChange():
    global controller
    controller.refreshData()

    action = request.form['range_change_button']
    if action == "min_up":
        controller.changeMinTemp(True)
    elif action == "min_down":
        controller.changeMinTemp(False)
    elif action == "max_up":
        controller.changeMaxTemp(True)
    elif action == "max_down":
        controller.changeMaxTemp(False)
    return redirect('/')


@app.route('/inTempFigUpdate')
def inTempFigUpdate():
    return Response(figureGenerator("in_temp.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inHumFigUpdate')
def inHumFigUpdate():
    return Response(figureGenerator("in_hum.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inACSFigUpdate')
def inACSFigUpdate():
    return Response(figureGenerator("in_air_cond_state.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/exTempFigUpdate')
def exTempFigUpdate():
    return Response(figureGenerator("ex_temp.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

def figureGenerator(figureName):
    try:
        frame = open('static/images/charts/'+figureName, 'rb').read()
        yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
    except:
        None

if __name__ == '__main__':
    app.run('localhost', 5000 ,use_reloader=True, use_debugger=True, use_evalex=True, debug=True)
