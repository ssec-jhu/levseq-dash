#
# globals.py
#

import requests

# app strings
web_title = "LevSeq remote test client"
flask_session_key = b"\xd6\x70\x04\xab\xd2\x08\x42\xe1\xa3\x5d\xfe\x1c\xce\x78\xd4\x7a"  # uuid.uuid4().hex

# URL parameters for production
#
# We use an external service to avoid complications when a local router exposes the public
#  IP address.  If ipinfo.io ever goes away, there are other services available.
resp = requests.get("http://ipinfo.io")
prodHost = resp.json()["hostname"]
prodPort = 8050

# URL parameters for debugging
devHost = "localhost"
devPort = 8052

# LevSeq webservice URL
lswsurl = "http://hplc-pc.che.caltech.edu:8051"
