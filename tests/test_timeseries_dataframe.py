# Copyright (c) 2024, Zong-han, Xie <zonghanxie@proton.me>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import contextlib
from io import StringIO
import unittest

import numpy as np

from modmesh import SimpleArrayUint64, SimpleArrayFloat64


class TimeSeriesDataFrame(object):

    def __init__(self):

        self._init_members()

    def _init_members(self):

        self._columns = list()
        self._index_data = None
        self._index_name = None
        self._data = list()

    def read_from_text_file(
        self,
        fname,
        delimiter=',',
        timestamp_in_file=True,
        timestamp_column=None
    ):
        """
        Generate dataframe from a text file.

        :param fname: path to the text file.
        :type fname: str | Iterable[str] | io.StringIO
        :param delimiter: delimiter.
        :type delimiter: str
        :param timestamp_in_file: If the text file containing index column,
                   data in this column expected to be integer.
        :type timestamp_in_file: bool
        :prarm timestamp_column: Column which stores timestamp data.
        :type timestamp_column: str
        :return: None
        """

        if isinstance(fname, str):
            if not os.path.exists(fname):
                raise Exception("Text file '{}' does not exist".format(fname))
            fid = open(fname, 'rt')
            fid_ctx = contextlib.closing(fid)
        else:
            fid = fname
            fid_ctx = contextlib.nullcontext(fid)

        with fid_ctx:
            fhd = iter(fid)

            index_column_num = 0 if timestamp_in_file else None

            table_header = [
                x.strip() for x in next(fhd).strip().split(delimiter)
            ]
            nd_arr = np.genfromtxt(fhd, delimiter=delimiter)

            if timestamp_in_file:
                if timestamp_column in table_header:
                    index_column_num = table_header.index(timestamp_column)
                self._index_data = SimpleArrayUint64(
                    array=nd_arr[:, index_column_num].astype(np.uint64)
                )
                self._index_name = table_header[index_column_num]
            else:
                self._index_data = SimpleArrayUint64(
                    array=np.arange(nd_arr.shape[0]).astype(np.uint64)
                )
                self._index_name = "Index"

            self._columns = table_header
            if index_column_num is not None:
                self._columns.pop(index_column_num)


            for i in range(nd_arr.shape[1]):
                if i != index_column_num:
                    self._data.append(
                        SimpleArrayFloat64(array=nd_arr[:, i].copy())
                    )

    def __getitem__(self, name):
        if name not in self._columns:
            raise Exception("Column '{}' does not exist".format(name))
        return self._data[self._columns.index(name)].ndarray

    @property
    def columns(self):
        return self._columns

    @property
    def shape(self):
        return (self._index_data.ndarray.shape[0], len(self._data))

    @property
    def index(self):
        return self._index_data.ndarray


class TimeSeriesDataFrameTC(unittest.TestCase):
    TESTDIR = os.path.abspath(os.path.dirname(__file__))
    DATADIR = os.path.join(TESTDIR, "data")
    columns_sol = [
        'DATA_DELTA_VEL[1]', 'DATA_DELTA_VEL[2]',
        'DATA_DELTA_VEL[3]', 'DATA_DELTA_ANGLE[1]',
        'DATA_DELTA_ANGLE[2]', 'DATA_DELTA_ANGLE[3]'
    ]

    columns_sol2 = [
        'DATA_DELTA_VEL[1]', 'DATA_DELTA_VEL[2]',
        'TIME_NANOSECONDS_TAI', 'DATA_DELTA_VEL[3]',
        'DATA_DELTA_ANGLE[1]', 'DATA_DELTA_ANGLE[2]',
        'DATA_DELTA_ANGLE[3]'
    ]

    dlc_data = """TIME_NANOSECONDS_TAI ,DATA_DELTA_VEL[1] ,DATA_DELTA_VEL[2] ,DATA_DELTA_VEL[3] ,DATA_DELTA_ANGLE[1] ,DATA_DELTA_ANGLE[2] ,DATA_DELTA_ANGLE[3]
1.6025960102293e+18,-0.18792724609375,-0.00048828125,-0.0478515625,-1.9073486328125e-06,3.814697265625e-06,1.9073486328125e-06
1.60259601024931e+18,-0.1903076171875,-0.0009765625,-0.0489501953125,1.9073486328125e-06,1.9073486328125e-06,0
1.60259601026931e+18,-0.18743896484375,0.0006103515625,-0.0498046875,0,1.9073486328125e-06,-1.9073486328125e-06
1.60259601028932e+18,-0.18927001953125,-0.0009765625,-0.04840087890625,-1.9073486328125e-06,3.814697265625e-06,1.9073486328125e-06
1.60259601030931e+18,-0.188720703125,-0.00103759765625,-0.0504150390625,0,-1.9073486328125e-06,0
1.60259601032931e+18,-0.18951416015625,-0.000732421875,-0.0489501953125,1.9073486328125e-06,3.814697265625e-06,0
1.60259601034931e+18,-0.18902587890625,-0.000732421875,-0.0489501953125,-1.9073486328125e-06,1.9073486328125e-06,0
1.6025960103693e+18,-0.1895751953125,-0.00128173828125,-0.04925537109375,0,0,-1.9073486328125e-06
1.60259601038931e+18,-0.18841552734375,6.103515625e-05,-0.0489501953125,0,3.814697265625e-06,0
1.60259601040931e+18,-0.1884765625,-0.00042724609375,-0.04840087890625,-1.9073486328125e-06,0,-1.9073486328125e-06
"""
    modified_dlc_data = """DATA_DELTA_VEL[1] ,DATA_DELTA_VEL[2] ,TIME_NANOSECONDS_TAI ,DATA_DELTA_VEL[3] ,DATA_DELTA_ANGLE[1] ,DATA_DELTA_ANGLE[2] ,DATA_DELTA_ANGLE[3]
-0.18792724609375,-0.00048828125,1602596010229299968,-0.0478515625,-1.9073486328125e-06,3.814697265625e-06,1.9073486328125e-06
-0.1903076171875,-0.0009765625,1602596010249309952,-0.0489501953125,1.9073486328125e-06,1.9073486328125e-06,0.0
-0.18743896484375,0.0006103515625,1602596010269309952,-0.0498046875,0.0,1.9073486328125e-06,-1.9073486328125e-06
-0.18927001953125,-0.0009765625,1602596010289319936,-0.04840087890625,-1.9073486328125e-06,3.814697265625e-06,1.9073486328125e-06
-0.188720703125,-0.00103759765625,1602596010309309952,-0.0504150390625,0.0,-1.9073486328125e-06,0.0
-0.18951416015625,-0.000732421875,1602596010329309952,-0.0489501953125,1.9073486328125e-06,3.814697265625e-06,0.0
-0.18902587890625,-0.000732421875,1602596010349309952,-0.0489501953125,-1.9073486328125e-06,1.9073486328125e-06,0.0
-0.1895751953125,-0.00128173828125,1602596010369299968,-0.04925537109375,0.0,0.0,-1.9073486328125e-06
-0.18841552734375,6.103515625e-05,1602596010389309952,-0.0489501953125,0.0,3.814697265625e-06,0.0
-0.1884765625,-0.00042724609375,1602596010409309952,-0.04840087890625,-1.9073486328125e-06,0.0,-1.9073486328125e-06
"""

    def test_read_from_text_file_basic(self):
        tsdf = TimeSeriesDataFrame()

        tsdf.read_from_text_file(
            StringIO(self.dlc_data)
        )
        self.assertEqual(tsdf._columns, self.columns_sol)
        self.assertEqual(len(tsdf._columns), 6)
        for i in range(len(tsdf._columns)):
            self.assertEqual(tsdf._data[i].ndarray.shape[0], 10)
        self.assertEqual(tsdf._index_name, 'TIME_NANOSECONDS_TAI')

        tsdf.read_from_text_file(
            StringIO(self.modified_dlc_data),
            delimiter=',',
            timestamp_column='TIME_NANOSECONDS_TAI'
        )

        self.assertEqual(tsdf._columns, self.columns_sol)
        self.assertEqual(len(tsdf._columns), 6)
        for i in range(len(tsdf._columns)):
            self.assertEqual(tsdf._data[i].ndarray.shape[0], 10)
        self.assertEqual(tsdf._index_name, 'TIME_NANOSECONDS_TAI')

        tsdf.read_from_text_file(
            StringIO(self.modified_dlc_data),
            delimiter=',',
            timestamp_in_file=False
        )
        self.assertEqual(tsdf._columns, self.columns_sol2)
        self.assertEqual(len(tsdf._columns), 7)
        for i in range(len(tsdf._columns)):
            self.assertEqual(tsdf._data[i].ndarray.shape[0], 10)
        self.assertEqual(tsdf._index_name, 'Index')

    def test_dataframe_attribute_columns(self):
        tsdf = TimeSeriesDataFrame()
        tsdf.read_from_text_file(
            StringIO(self.dlc_data)
        )
        self.assertEqual(tsdf.columns, self.columns_sol)

    def test_dataframe_attribute_shape(self):
        tsdf = TimeSeriesDataFrame()
        tsdf.read_from_text_file(
            StringIO(self.dlc_data)
        )
        self.assertEqual(tsdf.shape, (10, 6))

    def test_dataframe_attribute_index(self):
        tsdf = TimeSeriesDataFrame()
        tsdf.read_from_text_file(
            StringIO(self.dlc_data)
        )

        nd_arr = np.genfromtxt(
            StringIO(self.dlc_data), delimiter=','
        )[1:]

        self.assertEqual(
            list(tsdf.index), list(nd_arr[:, 0].astype(np.uint64))
        )

    def test_dataframe_get_column(self):
        tsdf = TimeSeriesDataFrame()
        tsdf.read_from_text_file(
            StringIO(self.dlc_data)
        )

        col_data = tsdf['DATA_DELTA_VEL[1]']

        nd_arr = np.genfromtxt(
            StringIO(self.dlc_data), delimiter=','
        )[1:]

        self.assertEqual(list(col_data), list(nd_arr[:, 1]))
