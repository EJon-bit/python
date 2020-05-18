import socketio

# standard Python
sio = socketio.Client()


@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

# sio.emit('my message', {'foo': 'bar'})

@sio.on('triggerRgb')
def on_message(data):
    print('RGB has been triggered', data)

    
sio.connect('http://localhost:5000')


sio.wait()