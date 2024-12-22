#
# fsexec.py
#

# The file upload mechanism is a bit clunky:
#
# - Ideally we would use the usual HTTP file-upload mechanisms to drop an uploaded file
#    into the filesystem where the postgres database server can find it.  But it is
#    awkward to route the upload from the remote client's browser to its web server and
#    then to this webservice.
#
# - The files to be uploaded are relatively small non-binary files whose contents are
#    delivered to the remote web server by a Plotly Dash Upload component as python
#    strings.  We assume these can be transmitted as "parameters" in an HTTP request
#    to this webservice.
# 
#  - But... we need to create a directory in which we can create a file whose permissions
#     let the postgres server process read it.  If we simply pass the file contents as a
#     parameter to a postgres SQL function, we need to write the file with a clunky
#     dynamic SQL "copy to" command.  We also have to struggle with creating the directory
#     and setting its permissions.
#
# To avoid all that, we handle the filesystem management and file creation here.  (We
#  assume that our linux system login gives us access to the postgres server's filesystem.)
#  Then we pass things to the postgres server for subsequent processing of the file.
#
# This puts some constraints on the arguments passed with "upload" requests:
#  args[0]: int  LevSeq user ID
#  args[1]: int  LevSeq group ID
#  args[2]: str  upload filename
#  args[3]: str  upload file contents
#  ...           ...
#
# Furthermore, we need to pass a directory path to the postgres server. 
# 
# Do this in two steps:
#  - ask pg to verify uniqueness (gid+filename); if this succeeds, pg saves the filename in v1.experiment_files
#  We do this
#  by injecting an additional argument to the list.  This means the resulting SQL
#  function signature must start like this:
#
#    in _dirpath text,
#    in _uid int,
#    in _eid int,
#    in _filename text,
#    in _filedata text
#
# (See the implementation of the SQL function upload_experiment_file for an example.)
#

import dbexec

    def UploadFile(args: dbexec.Arglist) -> str:

        # build the filespec using the current system user and the specified user's group
    ### TODO: QUERY FOR THE USER'S GROUP NAME!!!
        filespec = f""
        filespec = dbexec.QueryScalar( "peek_current_user", None )

        # verify that the specified file is not a duplicate
        if dbexec.QueryScalar( "is_experiment_file_unique", [filespec])

        return filespec;
