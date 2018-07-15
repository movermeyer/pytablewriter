# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, print_function, unicode_literals

from textwrap import dedent

import pytablewriter
import pytest

from ._common import print_test_result
from .data import (
    Data,
    header_list,
    mix_header_list,
    mix_value_matrix,
    null_test_data_list,
    value_matrix,
    value_matrix_iter,
    value_matrix_with_none,
)


try:
    import numpy as np
    import pandas

    SKIP_DATAFRAME_TEST = False
except ImportError:
    SKIP_DATAFRAME_TEST = True


normal_test_data_list = [
    Data(
        table="table-name ho'ge",
        indent=0,
        header=header_list,
        value=value_matrix,
        expected=dedent(
            """\
            table_name_ho_ge = pd.DataFrame([
                [1, 123.1, "a", 1, 1],
                [2, 2.2, "bb", 2.2, 2.2],
                [3, 3.3, "ccc", 3, "cccc"],
            ], columns=["a", "b", "c", "dd", "e"])

            """
        ),
    ),
    Data(
        table="tablename",
        indent=0,
        header=header_list,
        value=None,
        expected=dedent(
            """\
            tablename = pd.DataFrame([
            ], columns=["a", "b", "c", "dd", "e"])

            """
        ),
    ),
    Data(
        table="table with%null-value",
        indent=0,
        header=header_list,
        value=value_matrix_with_none,
        expected=dedent(
            """\
            table_with_null_value = pd.DataFrame([
                [1, None, "a", 1, None],
                [None, 2.2, None, 2.2, 2.2],
                [3, 3.3, "ccc", None, "cccc"],
                [None, None, None, None, None],
            ], columns=["a", "b", "c", "dd", "e"])

            """
        ),
    ),
    Data(
        table="tablename",
        indent=0,
        header=mix_header_list,
        value=mix_value_matrix,
        expected=dedent(
            """\
            tablename = pd.DataFrame([
                [1, 1.1, "aa", 1, 1, True, np.inf, np.nan, 1, dateutil.parser.parse("2017-01-01T00:00:00")],
                [2, 2.2, "bbb", 2.2, 2.2, False, np.inf, np.nan, np.inf, "2017-01-02 03:04:05+09:00"],
                [3, 3.33, "cccc", -3, "ccc", True, np.inf, np.nan, np.nan, dateutil.parser.parse("2017-01-01T00:00:00")],
            ], columns=["i", "f", "c", "if", "ifc", "bool", "inf", "nan", "mix_num", "time"])

            """
        ),
    ),
    Data(
        table="float-with-null",
        indent=0,
        header=["a", "b"],
        value=[
            ["0.03785679191278808", "826.21158713263"],
            [None, "826.21158713263"],
            [0.1, "1.0499675627886724"],
        ],
        expected=dedent(
            """\
            float_with_null = pd.DataFrame([
                [0.03785679191278808, 826.21158713263],
                [None, 826.21158713263],
                [0.1, 1.0499675627886724],
            ], columns=["a", "b"])

            """
        ),
    ),
    Data(
        table="empty header",
        indent=0,
        header=[],
        value=value_matrix,
        expected=dedent(
            """\
            empty_header = pd.DataFrame([
                [1, 123.1, "a", 1, 1],
                [2, 2.2, "bb", 2.2, 2.2],
                [3, 3.3, "ccc", 3, "cccc"],
            ])

            """
        ),
    ),
]

exception_test_data_list = [
    Data(
        table="dummy",
        indent=normal_test_data_list[0].indent,
        header=[],
        value=[],
        expected=pytablewriter.EmptyTableDataError,
    ),
    Data(
        table="",
        indent=normal_test_data_list[0].indent,
        header=normal_test_data_list[0].header,
        value=normal_test_data_list[0].value,
        expected=pytablewriter.EmptyTableNameError,
    ),
]

table_writer_class = pytablewriter.PandasDataFrameWriter


class Test_PandasDataFrameWriter_write_new_line(object):
    def test_normal(self, capsys):
        writer = table_writer_class()
        writer.write_null_line()

        out, _err = capsys.readouterr()
        assert out == "\n"


class Test_PandasDataFrameWriter_write_table(object):
    @pytest.mark.parametrize(
        ["table", "indent", "header", "value", "expected"],
        [
            [data.table, data.indent, data.header, data.value, data.expected]
            for data in normal_test_data_list
        ],
    )
    def test_normal(self, capsys, table, indent, header, value, expected):
        writer = table_writer_class()
        writer.table_name = table
        writer.set_indent_level(indent)
        writer.header_list = header
        writer.value_matrix = value
        writer.write_table()

        out, err = capsys.readouterr()
        print_test_result(expected=expected, actual=out, error=err)

        assert out == expected

    @pytest.mark.parametrize(
        ["table", "indent", "header", "value", "expected"],
        [
            [data.table, data.indent, data.header, data.value, data.expected]
            for data in exception_test_data_list
        ],
    )
    def test_exception(self, table, indent, header, value, expected):
        writer = table_writer_class()
        writer.table_name = table
        writer.set_indent_level(indent)
        writer.header_list = header
        writer.value_matrix = value

        with pytest.raises(expected):
            writer.write_table()


class Test_PandasDataFrameWriter_write_table_iter(object):
    @pytest.mark.parametrize(
        ["table", "header", "value", "expected"],
        [
            [
                "tablename",
                ["ha", "hb", "hc"],
                value_matrix_iter,
                dedent(
                    """\
                tablename = pd.DataFrame([
                    [1, 2, 3],
                    [11, 12, 13],
                    [1, 2, 3],
                    [11, 12, 13],
                    [101, 102, 103],
                    [1001, 1002, 1003],
                ], columns=["ha", "hb", "hc"])

                """
                ),
            ]
        ],
    )
    def test_normal(self, capsys, table, header, value, expected):
        writer = table_writer_class()
        writer.table_name = table
        writer.header_list = header
        writer.value_matrix = value
        writer.iteration_length = len(value)
        writer.write_table_iter()

        out, _err = capsys.readouterr()

        assert out == expected

    @pytest.mark.parametrize(
        ["table", "header", "value", "expected"],
        [[data.table, data.header, data.value, data.expected] for data in null_test_data_list],
    )
    def test_exception(self, table, header, value, expected):
        writer = table_writer_class()
        writer.table_name = table
        writer.header_list = header
        writer.value_matrix = value

        with pytest.raises(expected):
            writer.write_table_iter()


@pytest.mark.skipif("SKIP_DATAFRAME_TEST is True")
class Test_PandasDataFrameWriter_from_dataframe(object):
    @pytest.mark.parametrize(
        ["table", "expected"],
        [
            [
                "tablename",
                dedent(
                    """\
                tablename = pd.DataFrame([
                    [1, 0.125, "aa", 1, 1, True, np.inf, np.nan, 1, dateutil.parser.parse("2017-01-01T00:00:00")],
                    [2, 2.2, "bbb", 2.2, 2.2, False, np.inf, np.nan, np.inf, dateutil.parser.parse("2017-01-02T03:04:05+0900")],
                    [3, 3333.3, "cccc", -3, "ccc", True, np.inf, np.nan, np.nan, dateutil.parser.parse("2017-01-01T00:00:00")],
                ], columns=["i", "f", "c", "if", "ifc", "bool", "inf", "nan", "mix_num", "time"])

                """
                ),
            ]
        ],
    )
    def test_normal(self, capsys, table, expected):
        import dateutil
        from typepy import Integer, RealNumber

        writer = table_writer_class()
        writer.table_name = table
        writer.from_dataframe(
            pandas.DataFrame(
                [
                    [
                        1,
                        0.125,
                        "aa",
                        1.0,
                        "1",
                        True,
                        np.inf,
                        np.nan,
                        1,
                        dateutil.parser.parse("2017-01-01T00:00:00"),
                    ],
                    [
                        2,
                        2.2,
                        "bbb",
                        2.2,
                        "2.2",
                        False,
                        np.inf,
                        np.nan,
                        np.inf,
                        dateutil.parser.parse("2017-01-02T03:04:05+0900"),
                    ],
                    [
                        3,
                        3333.3,
                        "cccc",
                        -3.0,
                        "ccc",
                        True,
                        np.inf,
                        np.nan,
                        np.nan,
                        dateutil.parser.parse("2017-01-01T00:00:00"),
                    ],
                ],
                columns=["i", "f", "c", "if", "ifc", "bool", "inf", "nan", "mix_num", "time"],
            )
        )

        assert writer.value_matrix is not None
        assert writer.type_hint_list == [
            Integer,
            RealNumber,
            None,
            RealNumber,
            None,
            None,
            RealNumber,
            RealNumber,
            RealNumber,
            None,
        ]

        writer.write_table()

        out, err = capsys.readouterr()
        print_test_result(expected=expected, actual=out, error=err)

        assert out == expected
