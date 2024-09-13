from flask import jsonify


def create_response(message, code=200, data=None):
    """
   Create a standardized JSON response.

   :param message: Response message (str)
   :param code: HTTP status code (default is 200)
   :param data: Data to be returned in the response (list, dict, or None)
   :return: JSON response
   """

    response = {
        "message": message,
        "code": code
    }

    if data is not None:
        response["data"] = data
    else:
        response["data"] = [] if isinstance(data, list) else {}

    return jsonify(response), code
