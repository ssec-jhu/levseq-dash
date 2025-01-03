#
# globals.py
#

import os
import pwd
import builtins
import requests
import fastapi

# webservice implementation ID string
wsid = f"LevSeq database web service (FastAPI v{fastapi.__version__})"

# linux username
linux_username = pwd.getpwuid(os.getuid()).pw_name

# URL parameters for production
#
# We use an external service to avoid complications when a local router exposes the public
#  IP address.  If ipinfo.io ever goes away, there are other services available.
resp = requests.get("http://ipinfo.io")
prodHost = resp.json()["hostname"]
prodPort = 8051

# URL parameters for debugging
devHost = "localhost"
devPort = 8052


# print with formatting consistent with gunicorn; ANSI terminal escape codes from here:
#  https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
def DebugPrint(*args, **kwargs):
    builtins.print("\x1B[38:5:178mlsws\x1B[0m:     ", end="")
    builtins.print(*args, **kwargs)
