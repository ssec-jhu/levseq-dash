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
type QueryResponse = ResultSet | Scalar | None
type Arglist = list[Scalar]


# TODO: CLEAN UP THE CODE A BIT AND WRITE AN INTELLIGENT COMMENT
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

    # def to_json(self):
    #     return json.dumps(
    #         self, default=lambda o: o.__dict__, sort_keys=False, indent=None
    #     )


# TODO: WRITE A "PING" TO THE LevSeq webservice
# TODO: VERIFY timestamp datatype!!!!!!!


# HTTP POST to the LevSeq webservice
#
# Return value depends on verb prefix (see below):
#   - get:              ResultSet
#   - do, save:         None
#   - is, peek, upload: Scalar
#
def Query(verb: str, params: list[Scalar]) -> QueryResponse:

    pkg = QueryPackage(verb, params)
    # resp = requests.post(gv.lswsurl, pkg.to_json())
    resp = requests.post(gv.lswsurl, json=pkg)
    if not resp.ok:
        j = resp.json()
        raise ValueError(j["detail"])

    # cr = json.loads(resp.text)
    cr = resp.json()
    ##    return cr["columns"], cr["rows"]

    # extract the verb prefix:
    #  ^     start at the beginning of the string
    #  \w+?  one or more alphanumeric characters, non-greedy capture
    #  _     followed by underscore
    m = re.match(r"^(\w+?)_", verb)

    if m != None:

        # return according to the prefix
        try:
            match m[1]:
                case "get":
                    return cr["columns"], cr["rows"]

                case "do" | "save":
                    return None

                case "is" | "peek" | "upload":
                    return cr["details"]

                case _:
                    pass

        except Exception as ex:
            raise

    # at this point the prefix is invalid
    raise ValueError(f"invalid request verb '{verb}'")


# def NonQuery(verb: str, args: Arglist = []) -> None:
#     _doQuery(verb, args)
#     return None


# # execute a postgres SQL function that returns a rowset (result set)
# def Query(verb: str, args: Arglist = []) -> ResultSet:
#     return _doQuery(verb, args)  # type:ignore


# # execute a postgres SQL function that returns a scalar (number or string)
# def QueryScalar(verb: str, args: Arglist = []) -> Scalar:
#     j = _doQuery(verb, args)
#     return json.loads(j)  # type:ignore
