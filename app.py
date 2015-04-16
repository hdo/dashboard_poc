from gevent import monkey
monkey.patch_all()

import time
import random
from threading import Thread
from flask import Flask, render_template, session, request
from flask.ext.socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(3)
        count += 1
        if socketio:
            socketio.emit('data_response',
                          {'data': '%d W' % random.randrange(1,10000), 'count': count},
                          namespace='/test')

@app.route('/')
def index():
#    global thread
#    if thread is None:
#        thread = Thread(target=background_thread)
#        thread.start()
    print "index requested!"
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':

    # start worker thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()

    socketio.run(app, host="0.0.0.0", port=8080)
