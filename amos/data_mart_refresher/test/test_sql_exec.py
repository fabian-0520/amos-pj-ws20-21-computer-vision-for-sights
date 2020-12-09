from mock import patch
from data.sql_exec import exec_sql
from data.config import config


class CursorMock:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def execute(self, sql_string):
        pass

    def fetchone(self):
        return ['Tokyo']

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


class ConnectionExceptionMock:
    autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def cursor(self):
        return CursorExceptionMock()


class CursorExceptionMock(CursorMock):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def execute(self, sql_string):
        raise Exception('SELECT abc FROM xyz')


def test_exec_sql():
    db_dict = config(filename='database.ini')

    with patch('data.sql_exec.connect', return_value=ConnectionMock()) as connection_mock, \
            patch('data.sql_exec.config', return_value=db_dict) as config_mock:
        assert (connection_mock.called or config_mock.called) is False
        result = exec_sql('SELECT abc FROM xyz', True)
        assert (connection_mock.called and config_mock.called)
        assert result == 'Tokyo'


def test_exec_sql_error():
    db_dict = config(filename='database.ini')

    with patch('data.sql_exec.connect', return_value=ConnectionExceptionMock()) as connection, \
            patch('data.sql_exec.config', return_value=db_dict):
        assert connection.commit.called is False
        exec_sql('SELECT abc FROM xyz', True)
        assert connection.commit.called is False
