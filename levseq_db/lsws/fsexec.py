#
# fsexec.py
#

# There are two or more files associated with each LevSeq experiment:
#
#  - experimental data (*.csv): 1-3MB
#  - protein databank file (*.pdb): 100-300KB
#  - crystallographic information file (*.cif): 100-300KB
#
# Since any of these three files may need to be served out to a remote client, we need
#  to archive them somewhere:
#
#   - As postgres BLOBs: apart from initially loading the .csv data into relational
#      tables, we have no requirement for doing relational operations on the contents
#      of these files. So simplicity and performance become priorities, and in this
#      regard, the filesystem is significantly more performant than postgres BLOBs:
#      https://www.cybertec-postgresql.com/en/binary-data-performance-in-postgresql
#
#   - As filesystem files: better performance, but a bit of a pain to organize within a
#      linux filesystem, since we have to worry about filenames, hierarchical directory
#      structure, and permissions.
#
# Given that we choose to archive the files in the linux filesystem, the file upload
#  mechanism implemented here is a bit clunky:
#
# - We might use the usual HTTP 'multipart/form-data' request mechanism to ship
#    filename-plus-content from the remote client's browser to its web server and then
#    to this webservice.  Easier said than done, however, because the web application
#    would need to manage HTTP requests and responses to forward the files to the
#    webservice.
#
# - Fortunately, the files to be uploaded are small enough to be delivered by a Plotly
#    Dash Upload component as python strings, so we assume that we can then use the same
#    implementation to upload file contents to the webservice as we use to execute
#    database queries.
#
# - We also assume that this webservice has access to a filesystem that the postgres
#    server can read.  That's a reasonable assumption since we already assume that we
#    can run the webservice using linux system credentials that are also authenticated
#    as a postgres user (e.g., "lsdb").
#
# - So... in this implementation we piggyback file-management code onto the "usual"
#    database queries sent from web application server.  The query parameters contain
#    both file contents and file metadata.  (It might also be possible to pass the file
#    contents as a parameter to a postgres SQL function, but a postgres implementation
#    would require a clunky dynamic SQL "copy to" command.  It would also be hard to
#    create directories and set linux permissions.)
#
# Our strategy is thus to handle filesystem management and file creation here, and then
#  to pass things to the postgres server for subsequent processing of each file:
#
#  - query the postgres server to verify that the experiment/group/filename tuple is
#     unique, and to build the corresponding upload directory path
#
#  - create the file
#
#  - query the postgres server again to load file metadata (and, for .csv files, to
#     load file contents into SQL tables)
#

import pathlib
import base64
import fastapi
import dbexec


# Upload a file to the webservice/database server filesystem and update the
#  database contents accordingly.
#
#       args[0]: int  LevSeq user ID
#       args[1]: int  LevSeq group ID
#       args[2]: str  filename
#       args[3]: str  file contents        [upload only]
#
# fmt: off
def LoadFile(params: dbexec.Arglist) -> int:

    # query the database to validate the group/experiment/filename and obtain
    #  an upload filespec (i.e., a fully-qualified directory path and filename)
    dirpath = str(dbexec.QueryScalar("get_load_dirpath", params[:3]))  # type:ignore

    # create the upload directory
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)

    # convert to utf8 (which we need to do anyway if the file is base64-encoded)
    fileBytes = str(params[3]).encode("utf-8") #type:ignore

    # if the file content is base64-encoded, decode it
    c100 = fileBytes[:100]
    i = c100.find(b";base64,")
    if i > 0:
        # We want the os to write the base64-string as a sequence of bytes, so we encode
        #  the python string as 8-bit bytes, split it on the characters ';base64,', and
        #  grab just the utf8-encoded base64 string.
        copyFrom = base64.decodebytes(fileBytes[i+8:])
    
    else:
        # we presumably have plain text
        copyFrom = fileBytes

    # release no-longer-needed memory
    del fileBytes

    # write the text to the output file and save the number of bytes written
    filespec = f"{dirpath}{params[2]}" # type:ignore
    cbw = pathlib.Path(filespec).write_bytes(copyFrom)

    # load the file metadata (and, conditionally, the file contents) into the database
    cbl = dbexec.QueryScalar("load_file", [params[0], params[1], filespec] ) # type: ignore

    # verify that the number of characters loaded equals the number of characters written to the file
    if cbw != cbl:
        msg = f"{filespec}: {cbl} bytes loaded / {cbw} bytes written"
        raise fastapi.HTTPException(status_code=422, detail=msg)  # 422: Unprocessable Content        throw

    return cbw
# fmt: on


# Remove a file from the webservice/database server filesystem and update the database
#  contents accordingly.
#
#       args[0]: int  LevSeq user ID
#       args[1]: int  LevSeq group ID
#       args[2]: str  filename
#
def UnloadFile(params: dbexec.Arglist) -> str:

    # query the database to validate the group/experiment/filename and obtain
    #  a filespec (i.e., a fully-qualified directory path and filename)
    dirpath = str(dbexec.QueryScalar("get_unload_dirpath", params[:3]))  # type:ignore

    # zap the specified file if it exists
    filespec = f"{dirpath}{params[2]}"  # type:ignore
    pathlib.Path(filespec).unlink(missing_ok=True)

    # zap the experiment directory, too, if it exists and is empty
    p = pathlib.Path(dirpath)
    if p.exists() and not any(p.iterdir()):
        p.rmdir()

    # remove file metadata from the database
    return dbexec.NonQuery("unload_file", [params[0], params[1], filespec])  # type: ignore
