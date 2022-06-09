"""
This module contains the basic methods and some global constants for communicating web-server endpoints
 - specifically RosterServer.

Specific APIs are defined in other modules which build on this base-module.
"""

import requests
import traceback
from uuid import uuid4
from pprint import pprint, pformat
from requests.auth import HTTPBasicAuth


# CONSTANTS
AUTH = ("rosterUser", "n6kd8_4sa")
GET = "get"
POST = "post"  # insert
PUT = "put"    # update
DELETE = "delete"


def build_server_url(server):
    """
    :param server: A map with three keys: protocol, host, port.
    :return: A string representing the base path to the server - without the trailing slash.
    """

    protocol = server.get("protocol", "http")
    host = server["host"]
    port = server.get("port")
    port = (":%s" % port) if port else ""

    return "%s://%s%s" % (protocol, host, port)


def build_endpoint(server, path):
    """
    :param server: A map with three keys: protocol, host, port.
    :param path: A string representing a path beginning with a slash to the API endpoint.
    :return: A string representing the complete path to the API endpoint.
    """
    return "%s%s" % (build_server_url(server), path)


def http_json_request_response(server, path, method, data={}):
    """
    If any other response code than "200" is returned, then a basic Exception is raised.
    If parsing the JSON response fails, then a ValueError will be raised.

    :param server: A map with three keys: protocol, host, port.
    :param path: A string representing a path beginning with a slash to the API endpoint.
    :param method: A lower-case str representing a standard HTTP method: "get", "post", "put", "delete"
    :param data: An Python map, which will be converted to JSON and sent as the body of the request.
    :return: A Python map: the content of the body of the response, converted from JSON.
    """

    endpoint = build_endpoint(server, path)
    request_id = str(uuid4())
    print("  endpoint:   %s" % endpoint)
    print("  request-id: %s" % request_id)

    try:
        # request is a standard method available for python.
        res = requests.request(
                method,
                endpoint,
                headers={
                    "content-type": "application/json;charset=utf-8",
                    "accept": "application/json",
                    "request-id": request_id},
                auth=HTTPBasicAuth(*AUTH),  # SEIP requires HTTPBasicAuth
                json=data)

        if res.status_code == 200:
            if (not res.text) or res.text == "":
                print("  ## Warning: Request returned without content (200).")
                # 200 without content is not a successful update, return code 0.
                return {}, 0
            return res.json(), res.status_code

        elif res.status_code == 204:
            print("  ## Warning: Request returned without content (204).")
            return {}, res.status_code

        elif res.status_code not in [200, 204]:
            error_str = """Error occurred during interaction with Crew Info Server.
                    endpoint: %s
                      method: %s
                        code: %s
                        text: %s
                        """ % (endpoint,
                         method,
                         res.status_code,
                         res.text)
            print(" ERROR: %s" % error_str)
            return {}, res.status_code
    except TypeError as te:
        print(te)
        traceback.print_exc()
        return {}, 0
    except UnicodeDecodeError as ude:
        print(ude)
        traceback.print_exc()
        return {}, 0
    except Exception as e:
        print("  ## ERROR: http request method failed\n" + pprint(e))
        traceback.print_exc()
        return {}, 0
