from solve.db.base import BaseDatabase


class Database(BaseDatabase):
    def __init__(self, namespace, schema=None):
        super(Database, self).__init__(namespace, schema)
