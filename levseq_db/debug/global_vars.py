import os
import pwd

# app strings
web_title = "LevSeq Dashboard"  # TODO: is this good?
session_key = b"\xd6\x70\x04\xab\xd2\x08\x42\xe1\xa3\x5d\xfe\x1c\xce\x78\xd4\x7a"  # uuid.uuid4().hex

# form strings
experiment_name = "Experiment Name"
experiment_name_placeholder = "Enter a name for your experiment."

# DO NOT CHANGE
dbc_template_name = "flatly"

# linux username
linux_username = pwd.getpwuid(os.getuid()).pw_name

# LevSeq webservice URL
lswsurl = "http://hplc-pc.che.caltech.edu:8051"

# postgres database connection string
pgcs = f"user={linux_username} dbname=LevSeq"  # database connection string
schema = "v1"  # database schema
