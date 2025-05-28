from datetime import datetime

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