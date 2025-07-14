from datetime import datetime
from collections import defaultdict


#!!Warning that NA values now are -9999, TODO define new class with NA values
class DTFilter:

    def __init__(self, from_date: datetime = None, to_date: datetime = None):
        """Initialize the DTFilter with optional from and to dates."""
        self._from_date = from_date
        self._to_date = to_date

    @property
    def from_date(self):
        """Set the from date for the filter."""
        return self._from_date

    @from_date.setter
    def from_date(self, from_date: datetime) -> None:
        """Set the from date for the filter."""
        self._from_date = from_date

    @property  
    def to_date(self):
        """Get the to date for the filter."""
        return self._to_date
    
    @to_date.setter
    def to_date(self, to_date: datetime) -> None:
        """Set the to date for the filter."""
        self._to_date = to_date


class Statistics:

    @staticmethod
    def linear_regression(dataset: dict, column_index: int = 0, excel_date: bool=False) -> tuple:
        """Calculate a linear regression on the dataset (dict) provided.

        Args:
            dataset (dict): input dataset (from wellFilterData)
            column_index (int, optional): index of the column to use for regression. Defaults to 0.
            excel_date (bool, optional): whether to use 1970,1,1 as starting date or conform to excel dateformat (starting 1899,12,30). Defaults to False.

        Returns:
            tuple: with slope (a) and intercept (b) of the linear regression line.
        """
        def _excel_date(date1: datetime) -> float:

            # Initializing a reference date
            # Note that here date is not 31st Dec but 30th!
            temp = datetime(1899, 12, 30)
            delta = date1 - temp
            return float(delta.days) + (float(delta.seconds) / 86400)
        
        # Extract datetime and values from the dataset
        dates = []
        values = []
        for dt, vals in dataset.items():
            dates.append(dt)
            values.append(vals[column_index])
        # Convert datetimes to ordinal (float)
        if excel_date:
            print("Using Excel date format for regression.")
            X = [_excel_date(d) for d in dates]
        else:
            X = [d.toordinal() for d in dates]
        y = values
        n = len(X)
        if n == 0:
            raise ValueError("No data points found.")
        mean_x = sum(X) / n
        mean_y = sum(y) / n
        # Calculate slope (a) and intercept (b) using least squares
        numer = sum((X[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom = sum((X[i] - mean_x) ** 2 for i in range(n))
        if denom == 0:
            raise ValueError("Cannot compute a linear regression (zero variance in X).")
        a = numer / denom
        b = mean_y - a * mean_x
        return (a, b)
    
    @staticmethod
    def sum(dataset: dict, column_index: int = 0) -> float:
        """Calculate the sum of the values in the dataset.

        Args:
            dataset (dict): input dataset

        Returns:
            float: sum of the values
        """
        return sum(vals[column_index] for vals in dataset.values())
    
    @staticmethod
    def mean(dataset: dict, column_index: int = 0) -> float:
        """Calculate the mean of the values in the dataset.

        Args:
            dataset (dict): input dataset

        Returns:
            float: mean of the values
        """
        n = len(dataset)
        if n == 0:
            return 0.0
        return Statistics.sum(dataset, column_index) / n
    
    @staticmethod
    def min(dataset: dict, column_index: int = 0) -> float:
        """Calculate the minimum value in the dataset.

        Args:
            dataset (dict): input dataset

        Returns:
            float: minimum value
        """
        return min(vals[column_index] for vals in dataset.values())
    
    @staticmethod
    def max(dataset: dict, column_index: int = 0) -> float:
        """Calculate the maximum value in the dataset.

        Args:
            dataset (dict): input dataset

        Returns:
            float: maximum value
        """
        return max(vals[column_index] for vals in dataset.values())
    
class HydrologicalStatistics(Statistics):

    @staticmethod
    def GLG(dataset: dict, column_index: int = 0, num_hydrological_years: int = 8) -> float:
        """Calculate the Gemiddeld Laagste Grondwaterstand (GLG) for the dataset,
        as an 8-year average based on the hydrological year (April 1 - March 31).

        Args:
            dataset (dict): input dataset with datetime keys and list of values
            column_index (int, optional): index of the column to use. Defaults to 0.
            num_hydrological_years (int, optional): number of hydrological years to consider. Defaults to 8.

        Returns:
            float: GLG value
        """

        _v = HydrologicalStatistics.__last_sorted_items(dataset, column_index, num_hydrological_years, sort_from_low = True)

        if _v:
            return sum(_v) / len(_v)
        
    @staticmethod
    def GHG(dataset: dict, column_index: int = 0, num_hydrological_years: int = 8) -> float:
        """Calculate the Gemiddeld Hoogste Grondwaterstand (GHG) for the dataset,
        as an 8-year average based on the hydrological year (April 1 - March 31).

        Args:
            dataset (dict): input dataset with datetime keys and list of values
            column_index (int, optional): index of the column to use. Defaults to 0.
            num_hydrological_years (int, optional): number of hydrological years to consider. Defaults to 8.

        Returns:
            float: GHG value
        """
        _v = HydrologicalStatistics.__last_sorted_items(dataset, column_index, num_hydrological_years, sort_from_low = False)

        if _v != None:
            return sum(_v) / len(_v)
        else:
            return 0.0

    @staticmethod
    def __last_sorted_items(dataset: dict, column_index: int, num_hydrological_years: int, sort_from_low: bool = True) -> float:
        """_summary_

        Args:
            years_to_use (list): list of years to use
            yearly_values (dict): _description_
            sort_from_low (True): _description_

        Returns:
            list: _description_
        """
        # Sort hydrological years and select the most recent 8 years
        sorted_years = HydrologicalStatistics.__sorted_hydrological_year(dataset, column_index)
        if len(sorted_years.keys()) <= num_hydrological_years:
            print(f"Not enough years available for GLG calculation (only {len(sorted_years)}), using all available years.")
            return None
        print(sorted_years)
        years_to_use = sorted_years[-num_hydrological_years:]

        _v = []
        for year in years_to_use:
            values = sorted_years[year]
            if len(values) < 3:
                continue
            lowest_three = sorted(values, reverse = sort_from_low)[:3]
            _v.append(sum(lowest_three) / 3)

        if  _v:
            return _v
        else:
            return None

    @staticmethod
    def __sorted_hydrological_year(dataset: dict, column_index: int) -> dict:
        # For each hydrological year, get the 3 lowest values and average them
        yearly_values = HydrologicalStatistics.__hydrological_year(dataset, column_index)
        return {v: yearly_values[v] for v in sorted(yearly_values.keys())}
    
    @staticmethod
    def __hydrological_year(dataset: dict, column_index: int) -> dict:
        # Group values by hydrological year (April 1 - March 31)
        yearly_values = defaultdict(list)
        for dt, vals in dataset.items():
            hydro_year = dt.year if dt.month >= 4 else dt.year - 1
            yearly_values[hydro_year].append(vals[column_index])
        return yearly_values
    