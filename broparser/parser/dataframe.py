from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
from .statistics import Statistics

@dataclass
class wellFilterData:

    def __init__(self):
        self.columns: List = None
        self.dataset: Dict[datetime, float] = {}
        self.statistics = {}

    def add_observation(self, date_time: datetime|str, value: list, 
                        columns: List = None, return_errors: bool = False) -> None:
        """Append a new observation to the dataset. \n
        If the date_time is a string, it will be converted to a datetime object.

        Args:
            date_time (datetime | str): datetime of the observation
            value (list): value of the observation, must be a list of values
            columns (List, optional): set column names. Defaults to None.
            return_errors (bool, optional): if errors need to be returned, else None. Defaults to False.

        Returns:
            None or Exception: None or error message if return_errors is True.
        """
        if isinstance(date_time, str):
            date_time = datetime(year = int(date_time[:4]), month= int(date_time[5:7]), 
                         day = int(date_time[8:10]), hour = int(date_time[11:13]), 
                         minute = int(date_time[14:16]), second= int(date_time[17:19]))
        
        try:
            self.dataset[date_time] = value
        except Exception as e:
            print(f"Error adding observation: {date_time}, reason {e}")
            if return_errors:
                return e
            pass
        if columns != None:
            self.add_columns(columns)
        return None

    def subset_observations(self, start: datetime = None, end: datetime = None) -> Dict[datetime, float]:
        """Subset the observations based on a start and end datetime.

        Args:
            start (datetime, optional): Start datetime of dataset. Defaults to None.
            end (datetime, optional): End datetime dataset. Defaults to None.
        Returns:
            Dict: A subset of the dataset containing only the observations within the specified range.
        
        """
        ss = self.dataset
        self.__any_datacheck("No data in dataset, cannot subset")
        if start != None:
            ss = {k: v for (k, v) in ss.items() if k >= start}
        if end != None:
            ss = {k: v for (k, v) in ss.items() if k <= end}
        return ss
       
    def add_columns(self, columns: List) -> None:
        """Adds columns to the dataset. \n
        You can only append columns if there is data in the dataset

        Args:
            columns (List): Columns to append to dataset. \n
            Assert that length of columns is amount of fields in the dataset
        
        Returns:
            None
        """

        self.__any_datacheck("Couldn't set columns, no data in dataset yet")

        if len(self.dataset[list(self.dataset.keys())[0]]) + 1 == len(columns):
            self.columns = columns
        else:
            print("Columns of different length to dataset")
    
    def order(self):
        """Sort the dataset by datetime.

        Returns:
            Dict: Sorted dictionary by datetime.
        """
        self.dataset = dict(sorted(self.dataset.items(), key = lambda item: item[0]))
        return self.dataset
    
    def linear_regression(self, column_index: int = 0, excel_date: bool = False) -> tuple:
        """Calculate the linear regression of the dataset.

        Args:
            column_index (int, optional): index of the column to use for regression. Defaults to 0.
            excel_date (bool, optional): whether to use 1970,1,1 as starting date or conform to excel dateformat (starting 1899,12,30). Defaults to False.

        Returns:
            tuple: with slope (a) and intercept (b) of the linear regression line.
        """
        return Statistics.linear_regression(self.dataset, column_index, excel_date)	
    
    def sum(self, column_index: int = 0) -> float:
        """Calculate the sum of the values in the dataset.

        Args:
            column_index (int, optional): index of the column to use for sum. Defaults to 0.

        Returns:
            float: sum of the values in the specified column.
        """
        return Statistics.sum(self.dataset, column_index)
    
    def mean(self, column_index: int = 0) -> float:
        """Calculate the mean of the values in the dataset.

        Args:
            column_index (int, optional): index of the column to use for mean. Defaults to 0.

        Returns:
            float: mean of the values in the specified column.
        """
        return Statistics.mean(self.dataset, column_index)
    
    def calculate_statistics(self, column_index: int = 0) -> None:
        """Calculate statistics for the dataset and store them in the statistics attribute.

        Args:
            column_index (int, optional): indices of the column to use for statistics. Defaults to 0.
        
        Returns:
            None
        """

        self.statistics = {
            "sum": self.sum(column_index),
            "mean": self.mean(column_index),
            "linear_regression": self.linear_regression(column_index)
        }
        return self.statistics
    
    def __str__(self):
        print_str = ""
        if not self.columns == None:
            print_str += " ----- ".join([str(t) for t in self.columns]) + " \n"
            
        if self.__any_datacheck(""):
            if len(self.dataset) > 7:
                for i in list(self.dataset.keys())[:3]:
                    print_str += self.__printline(i)
                print_str += ".... \n"
                for i in list(self.dataset.keys())[-3:]:
                    print_str += self.__printline(i)
            else:
                for i in self.dataset.keys():
                    print_str += self.__printline(i)

        return print_str
    
    def __repr__(self):
        return str(self)
                    
    def __printline(self, i):
        if self.dataset[i] != None:
            if len(self.dataset[i]) > 0 or i != None:
                return f"{i}: {", ".join([str(t) for t in self.dataset[i] if t != None])} \n"

    def __len__(self):
        if self.dataset != None:
            return len(self.dataset.keys())
        else:
            return 0
        
    def __any_datacheck(self, message = ""):
        if len(self.dataset) > 0:
            return True
        else:
            raise ValueError(message)
