#
# wsexec.py
#

import re
import json
import requests
import global_vars as gv

# handy type aliases
type Scalar = int | float | str
type Rowset = list[tuple]
type Columns = list[str]
type ResultSet = tuple[Columns, Rowset]
type QueryResponse = ResultSet | Scalar
type Arglist = list[Scalar]


# TODO: CLEAN UP THE CODE A BIT AND WRITE AN INTELLIGENT COMMENT
# define a class that supports json serialization of HTTP request parameters
class QueryPackage(dict):

    verb: str
    params: list

    def __new__(cls, verb, params):
        instance = super(QueryPackage, cls).__new__(cls)
        return instance

    def __init__(self, verb, params):
        super().__init__(verb=verb, params=params)

        self.verb = verb
        self.params = params


# TODO: WRITE A "PING" TO THE LevSeq webservice
# TODO: VERIFY timestamp datatype!!!!!!!


# HTTP POST to the LevSeq webservice
#
def Query(verb: str, params: list[Scalar]) -> QueryResponse:

    pkg = QueryPackage(verb, params)
    resp = requests.post(gv.lswsurl, json=pkg)
    if not resp.ok:

        msg = f"LevSeq webservice response: {resp.status_code} {resp.reason}"
        if resp.text != "null":
            j = resp.json()
            msg += f": \n{j["detail"]}"

        raise ValueError(msg)

    # use the verb prefix to determine the type of the result set
    m = re.match(r"^(\w+?)_", verb)
    if m == None:
        raise ValueError(f"invalid request verb '{verb}'")

    # deserialize the json-formatted response
    j = resp.json()

    # "get_" queries return a ResultSet
    if m[1] == "get":
        return j["columns"], j["rows"]

    # all other queries return a Scalar (regardless of how the LevSeq webservice handles them)
    return j["details"]
