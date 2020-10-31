import sys
sys.path.append('resources/')
from controller import Controller
import time
from flask import Flask, render_template, request, redirect, Response

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

#Creates a controller instance
controller = Controller()

@app.route('/')
def index():
    global controller

    #Refresh sensors data to show
    try:
        controller.refreshData()
    except:
        None

    #Refresh page with new data
    return render_template('index.html', min = controller.getTempFormatted('MIN')
    , max = controller.getTempFormatted('MAX'), in_temp = controller.getTempFormatted('IN_TEMP')
    , in_hum = controller.getHumFormatted(), in_air_cond_state = controller.getAirCondState()
    , ex_temp = controller.getTempFormatted('EX_TEMP'))

@app.route('/rangeChange/', methods=['POST'])
def rangeChange():
    global controller

    #Gets action from POST action
    action = request.form['range_change_button']
    try:
        #Increase minimum temperature
        if action == "min_up":
            controller.changeMinTemp(True)
        #Decrease minimum temperature
        elif action == "min_down":
            controller.changeMinTemp(False)
        #Increase maximum temperature
        elif action == "max_up":
            controller.changeMaxTemp(True)
        #Decrease maximum temperature
        elif action == "max_down":
            controller.changeMaxTemp(False)
    except:
        None

    #Refresh page
    return redirect('/')


@app.route('/inTempFigUpdate')
#Loads internal temperature chart on page
def inTempFigUpdate():
    return Response(figureGenerator("in_temp.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inHumFigUpdate')
#Loads internal humidity chart on page
def inHumFigUpdate():
    return Response(figureGenerator("in_hum.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inACSFigUpdate')
#Loads internal air conditioner state chart on page
def inACSFigUpdate():
    return Response(figureGenerator("in_air_cond_state.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/exTempFigUpdate')
#Loads external temperature chart on page
def exTempFigUpdate():
    return Response(figureGenerator("ex_temp.png"), mimetype='multipart/x-mixed-replace; boundary=frame')

#Generate figure
def figureGenerator(figureName):
    try:
        frame = open('static/images/charts/'+figureName, 'rb').read()
        yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
    except:
        None

if __name__ == '__main__':
    app.run('localhost', 8000 ,use_reloader=True, use_debugger=True, use_evalex=True, debug=True)
