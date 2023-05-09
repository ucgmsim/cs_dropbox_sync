from functools import wraps

import flask


class MissingKeyError(Exception):
    def __init__(self, key):
        self.error_code = 400
        self.error_msg = f"Request is missing parameter: {key}"


def endpoint_exception_handling(app):
    def endpoint_exception_handling_decorator(f):
        """Handling exception for endpoints"""

        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                return f(*args, **kwargs)

            except MissingKeyError as ex:
                app.logger.error(ex.error_msg, exc_info=True)
                return flask.jsonify({"error": ex.error_msg}), ex.error_code
            except ValueError as ve:
                error_msg = str(ve)
                app.logger.error(error_msg, exc_info=True)
                return (
                    flask.jsonify({"error": error_msg}),
                    400,
                )
            except FileNotFoundError as ex:
                error_msg = f"Result file {ex.filename} does not exist."
                error_code = 404
                return flask.jsonify({"error": error_msg}), error_code
            except Exception as e:
                error_msg = str(e)
                error_code = 500
                return flask.jsonify({"error": error_msg}), error_code

        return decorated

    return endpoint_exception_handling_decorator
