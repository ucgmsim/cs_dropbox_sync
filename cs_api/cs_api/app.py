import argparse
from pathlib import Path

import yaml
from flask_cors import CORS
from OpenSSL import SSL

from cs_api.server import app

# Enable CORS for the Flask app
CORS(app, resources={r"/*": {"origins": "*"}})

# from OpenSSL import SSL
#
# context = SSL.Context(SSL.TLSv1_2_METHOD)
# context.use_privatekey_file("/home/joel/local/web_cybershake/server.key")
# context.use_certificate_file("/home/joel/local/web_cybershake/server.cert")

# Disable automatic upgrading of insecure requests to HTTPS
# @app.after_request
# def add_csp_header(response):
#     response.headers['Content-Security-Policy'] = "upgrade-insecure-requests;"
# document.querySelector('meta[http-equiv="Content-Security-Policy"]').remove();

#     return response

if __name__ == "__main__":
    with open(Path(__file__).resolve().parent / "api_config.yaml") as f:
        config = yaml.safe_load(f)

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--port",
        type=int,
        help="Port number, default: port number from the config file.",
        default=config["port"],
    )
    args = parser.parse_args()

    app.run(threaded=False, host="0.0.0.0", processes=config["n_procs"], port=args.port)
