"""This module contains the tests for the exec_sql module of the data sub-app."""
from data.exec_sql import exec_dml_query, exec_dql_query
from mock import patch
import pytest


def test_valid_dql_query(connection_mock):
    with patch('data.exec_sql.connect', return_value=connection_mock) as conn_mock, \
            patch('data.exec_sql.config', return_value={}) as config_mock:
        assert (conn_mock.called or config_mock.called) is False
        result = exec_dql_query('SELECT abc FROM xyz', True)
        assert conn_mock.called and config_mock.called
        assert result == [['Berlin'], ['Tokyo']]


@pytest.mark.parametrize('dml_query, filling_parameters', [
    ('INSERT INTO a VALUES ("b", "c")', None),
    ('INSERT INTO a VALUES ("%s", "%s")', ("b", "c"))
])
def test_valid_dml_query(connection_mock, dml_query, filling_parameters):
    with patch('data.exec_sql.connect', return_value=connection_mock) as conn_mock, \
            patch('data.exec_sql.config', return_value={}) as config_mock:
        assert (conn_mock.called or config_mock.called) is False
        exec_dml_query(dml_query, filling_parameters)
        assert conn_mock.called and config_mock.called


def test_invalid_query(connection_exception_mock):
    with patch('data.exec_sql.connect', return_value=connection_exception_mock) as conn_mock, \
            patch('data.exec_sql.config', return_value={}) as config_mock:
        assert (conn_mock.called or config_mock.called) is False
        exec_dql_query('SELECT abc FROM xyz', True)  # errors caught
        exec_dml_query('SELECT abc FROM xyz', True)
