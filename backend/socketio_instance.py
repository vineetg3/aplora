from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*",max_http_buffer_size=10 * 1024 * 1024)
