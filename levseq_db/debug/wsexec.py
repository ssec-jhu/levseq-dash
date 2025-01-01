#
# wsexec.py
#

import re
import requests
import globals as g

# handy type aliases
type Scalar = int | float | str
type Rowset = list[tuple]
type Columns = list[str]
type ResultSet = tuple[Columns, Rowset]
type QueryResponse = ResultSet | Scalar
type Arglist = list[Scalar]


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


# HTTP POST to the LevSeq webservice
#
def Query(verb: str, params: list[Scalar]) -> QueryResponse:

    # sanity check parameters
    if not isinstance(params, list) or not all(isinstance(p, (int, float, str)) for p in params):
        raise ValueError("query parameters are not list[Scalar]")

    # HTTP request/response
    pkg = QueryPackage(verb, params)
    resp = requests.post(g.lswsurl, json=pkg)
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
