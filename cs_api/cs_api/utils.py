from typing import List, Union, Tuple, Iterable, Type, Dict
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


def get_check_keys(
    data_dict: Dict,
    keys: Iterable[Union[str, Tuple[str, Type]]],
) -> List[str]:
    """Retrieves the specified keys from the data dict, throws a
    MissingKey exception if one of the keys does not have a value.

    If a type is specified with a key (as a tuple of [key, type]) then the
    value is also converted to the specified type
    """
    values = []
    for key_val in keys:
        # Check if a type is specified with the key
        if isinstance(key_val, tuple):
            cur_key, cur_type = key_val
        else:
            cur_key, cur_type = key_val, None

        value = data_dict.get(cur_key)
        if value is None:
            raise MissingKeyError(cur_key)

        # Perform a type conversion if one was given & append value
        values.append(value if cur_type is None else cur_type(value))
    return values
