#
# global_vars.py
#

import os
import pwd
import requests

# webservice implementation ID string
ws_id = "LevSeq web service"

# linux username
linux_username = pwd.getpwuid(os.getuid()).pw_name

# URL parameters for production
#
# We use an external service to avoid complications when a local router exposes the public
#  IP address.  If ipinfo.io goes away, there are other services available.
resp = requests.get("http://ipinfo.io")
prodHost = resp.json()["hostname"]
prodPort = 8051

# URL parameters for debugging
devHost = "localhost"
devPort = 8052
