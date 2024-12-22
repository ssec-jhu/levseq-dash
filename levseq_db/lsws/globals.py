#
# globals.py
#

import os
import pwd

# ID
ws_id = "LevSeq web service"
linux_username = pwd.getpwuid(os.getuid()).pw_name

# URL parameters for production
prodHost = "hplc-pc.che.caltech.edu"
prodPort = 8051

# URL parameters for debugging
devHost = "localhost"
devPort = 8052
