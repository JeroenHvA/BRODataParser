from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class wellFilterData:

    def __init__(self):
        self.columns: List = None
        self.dataset: Dict[datetime, float] = {}

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

class wellFilter:
    def __init__(self, gld_bro_id, well_number, well_bro_id):
        self.gld_bro_id = gld_bro_id ## common bro id
        self.well_number = well_number
        self.well_bro_id = well_bro_id ## unique bro id for this well
        ## metadata
        self.screen_length = None
        self.screen_top_position = None
        self.screen_bottom_position = None

        self.dataset = wellFilterData()  # dictionary with 

    def add_metadata(self, screen_length: float = None, screen_top_position:float = None, screen_bottom_position:float = None):
        """Add metadata to the well observation.

        Args:
            screen_length (float, optional): screen length of the filter. Defaults to None.
            screen_top_position (float, optional): top position of the filter. Defaults to None.
            screen_bottom_position (float, optional): bottom position of the filter. Defaults to None.
        """
        self.screen_length = screen_length
        self.screen_top_position = screen_top_position
        self.screen_bottom_position = screen_bottom_position

    def __str__(self):
        return f"well #{self.well_number} (brocom: {self.well_bro_id}, gldcommon:{self.gld_bro_id}): {len(self.dataset)} measurements"
