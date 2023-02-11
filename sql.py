from appdata import AppDataPaths
import os

# For the packaged binary, the sql.db cannot be located if the
# user tries to use ygo from a directory other than source.
# The install script adds a case for installing the data source
# to appdata. Use that sql copy if the local copy cannot be found.
#
# NOTE: If a name colission occurs b/w the database file an this filename,
# an error may occur as it tries to read from the unintended database file.
def sql_path():
    sql_fname = "yugioh_card_database.sql"
    local_cpy = os.path.join(os.getcwd(), sql_fname)
    appdata = AppDataPaths("ygo")
    appdata_cpy = os.path.join(appdata.app_data_path, sql_fname)
    if os.path.exists(local_cpy):
        return local_cpy
    elif os.path.exists(appdata_cpy):
        return appdata_cpy
    assert False, "No sql database found. Corrupted install."
