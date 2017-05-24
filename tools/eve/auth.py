# coding: utf-8


PERMISSION_ADD = 'add'          # for example: add to guest book at site by guest / or add order
PERMISSION_READ = 'read'        # read all and edit self
PERMISSION_EDIT = 'edit'        # modify all data, but cen not delete
PERMISSION_DELETE = 'delete'    # delete
PERMISSION_ALL = [PERMISSION_ADD, PERMISSION_READ, PERMISSION_EDIT, PERMISSION_DELETE]

# comparison request methods (CRUD) to permission
# http://python-eve.org/features.html#full-range-of-crud-operations
PERMISSION_REQUESTS = {
    'POST':   PERMISSION_ADD,      # INSERT
    'GET':    PERMISSION_READ,     # SELECT
    'PATCH':  PERMISSION_EDIT,     # UPDATE
    'PUT':    PERMISSION_EDIT,     # replace
    'DELETE': PERMISSION_DELETE,   # DELETE
}

