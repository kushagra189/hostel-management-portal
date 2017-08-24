from app import app as application
from flask_cors import CORS
CORS(application)

application.run(host='127.0.0.1', port = 5000, debug =True)
