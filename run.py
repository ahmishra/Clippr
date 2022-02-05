from app import app, db, socketio  # Imports (app, db, socketio)

DEBUG = True  # Debug mode (True or False)
HOST = "0.0.0.0"  # Host (Use 0.0.0.0 for external access)
PORT = 5000  # Port (Use any free port)

if __name__ == "__main__":  # If this file is run directly, run the app
    db.create_all()  # Create the database, if it doesn't exist already
    socketio.run(app, debug=DEBUG, host=HOST, port=PORT)  # Run the app (SOCKETIO)
