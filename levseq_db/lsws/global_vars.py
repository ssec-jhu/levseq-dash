#
# global_vars.py
#

import os
import pwd

# webservice implementation ID string
ws_id = "LevSeq web service"

# linux username
linux_username = pwd.getpwuid(os.getuid()).pw_name

# URL parameters for production
prodHost = "hplc-pc.che.caltech.edu"
prodPort = 8051

# URL parameters for debugging
devHost = "localhost"
devPort = 8052
