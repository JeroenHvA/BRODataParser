from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

from .dataframe import wellFilterData
from .statistics import HydrologicalStatistics as HStat

class wellFilter:
    def __init__(self, gld_bro_id, well_number, well_bro_id):

        #TODO: link to well object
        self.gld_bro_id = gld_bro_id ## common bro id
        self.well_number = well_number
        self.well_bro_id = well_bro_id ## unique bro id for this well
        ## metadata
        self.screen_length = None
        self.screen_top_position = None
        self.screen_bottom_position = None

        self.dataset = wellFilterData()  # dictionary with the data in a wellFilterData object 
        self.start_date = None
        self.end_date = None

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
    
    def subset_observations(self, start: datetime = None, end: datetime = None) -> Dict[datetime, float]:
        """Subset the observations based on a start and end datetime.

        Args:
            start (datetime, optional): Start datetime of dataset. Defaults to None.
            end (datetime, optional): End datetime dataset. Defaults to None.
        
        Returns:
            Dict: A subset of the dataset containing only the observations within the specified range.
        """
        self.dataset.order()
        return self.dataset.subset_observations(start, end)
    
    def get_start_date(self) -> datetime:
        """Get the start date of the dataset.

        Returns:
            datetime: Start date of the dataset.
        """
        if self.start_date == None:
            self.start_date = min(self.dataset.dataset.keys())
        return self.start_date
    
    def get_end_date(self) -> datetime:
        """Get the end date of the dataset.

        Returns:
            datetime: End date of the dataset.
        """
        if self.end_date == None:
            self.end_date = max(self.dataset.dataset.keys())
        return self.end_date

    def GLG(self, column_index: int = 0, num_hydrological_years: int = 8, start_from: datetime = None, end_from: datetime = None) -> float:
        """ Calculate the Gemiddeld Laagste Grondwaterstand (GLG) on the specific wellFilter

        Args:
            column_index (int8): The column that contains the data
            num_hydrological_years (int8): The amount of hydrological years to calculate GLG on. Defaults to 8
            start_from (datetime, optional): To subset from a specific start date. Defaults to None.
            end_from (datetime, optional): To subset from a specific end date. Defaults to None.

        Returns:
            float: GLG value
        """
        data = self.subset_observations(start_from, end_from)
        return HStat.GLG(data, column_index=column_index, num_hydrological_years=num_hydrological_years)
    
    def GHG(self, column_index: int = 0, num_hydrological_years: int = 8, start_from: datetime = None, end_from: datetime = None) -> float:
        """ Calculate the Gemiddeld Hoogste Grondwaterstand (GHG) on the specific wellFilter

        Args:
            column_index (int8): The column that contains the data
            num_hydrological_years (int8): The amount of hydrological years to calculate GLG on. Defaults to 8
            start_from (datetime, optional): To subset from a specific start date. Defaults to None.
            end_from (datetime, optional): To subset from a specific end date. Defaults to None.

        Returns:
            float: GHG value 
        """
        data = self.subset_observations(start_from, end_from)
        return HStat.GLG(data, column_index=column_index, num_hydrological_years=num_hydrological_years)
    
    
    def __repr__(self):
        return self.dataset.__repr__()

    def __str__(self):
        return f"well #{self.well_number} (brocom: {self.well_bro_id}, gldcommon:{self.gld_bro_id}): {len(self.dataset)} measurements"
