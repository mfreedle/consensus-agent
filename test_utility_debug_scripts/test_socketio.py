import socketio

# Replace with your actual JWT token and session_id
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MDc0MTI3OH0.c7-LOHuBOsplfo1I2_DAKu3QLp0PZFcdUdtZcEiTMzs"
SESSION_ID = 1  # Replace with a valid session_id

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")
    sio.emit("join", {"session_id": SESSION_ID})
    print("Joined session:", SESSION_ID)
    sio.emit("send_message", {
        "session_id": SESSION_ID,
        "message": "Hello from Python Socket.IO client!",
        "token": JWT_TOKEN
    })

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on("new_message")
def on_new_message(data):
    print("New message received:", data)

@sio.on("error")
def on_error(data):
    print("Error:", data)

if __name__ == "__main__":
    sio.connect("http://127.0.0.1:8000")
    sio.wait()