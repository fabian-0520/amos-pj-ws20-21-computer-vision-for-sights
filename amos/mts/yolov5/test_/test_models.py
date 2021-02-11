class CursorMock:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def execute(self, sql_string):
        pass

    def fetchall(self):
        return [['Berlin'], ['Tokyo']]

    def close(self):
        pass


class ConnectionMock:
    autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def cursor(self):
        return CursorMock()

    def commit(self):
        pass
