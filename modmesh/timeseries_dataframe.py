import os
import numpy as np

from modmesh import SimpleArrayFloat64


__all__ = [
    'TimeSeriesDataFrame'
]


class TimeSeriesDataFrame(object):
    
    def __init__(self):

        self.columns = list() # Column names
        self.inex_column = None
        self._data = None

    def read_from_text_file(self, txt_path: str, delimiter: str=',', time_stamp_included: bool = True):
        # read the first line as the 
        if not os.path.exists(txt_path):
            raise Exception("Text file '{}' does not exist".format(txt_path))
        
        # read the first line as columns and assuming the first column is timestamp
        with open(txt_path, 'r') as f:
            if time_stamp_included:
                # remove all leading/tail spaces in the column names
                self.columns = [x.strip() for x in f.readline().strip().split(delimiter)]
                self.inex_column = self.columns[0]
            else:
                # remove all leading/tail spaces in the column names
                self.columns = [x.strip() for x in f.readline().strip().split(delimiter)]
        
        nd_arr = np.genfromtxt(txt_path, delimiter=delimiter)[1:] # remove the first row which is the table header
        self._data = SimpleArrayFloat64(array=nd_arr)
