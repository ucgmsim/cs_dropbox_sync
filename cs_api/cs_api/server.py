import os
import logging
from pathlib import Path

import flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from cs_api.custom_log_handler import MultiProcessSafeTimedRotatingFileHandler


app = flask.Flask(str(Path(__file__).parent))
# Enable CORS for the Flask app
# CORS(app)
app.app_context().push()

logfile = os.path.join(os.path.dirname(__file__), "logs/logfile.log")
os.makedirs(os.path.dirname(logfile), exist_ok=True)

TRFhandler = MultiProcessSafeTimedRotatingFileHandler(filename=logfile, when="midnight")

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    level=logging.DEBUG,
    handlers=[TRFhandler],
)
logging.getLogger('flask_cors').level = logging.DEBUG

TRFhandler.setLevel(logging.DEBUG)
# To prevent having a same log twice
app.logger.propagate = False
app.logger.addHandler(TRFhandler)
logging.getLogger("matplotlib").setLevel(logging.ERROR)

# Connection details for the DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.environ["DB_PATH"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Add the endpoints
from cs_api.api import metadata, runs
