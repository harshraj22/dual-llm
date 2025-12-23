from ..base import BaseDataset, DataPoint
import math
import uuid

class PrimeDataset(BaseDataset):
    def __init__(self, range_start=1, range_end=20):
        self.raw_data = list(range(range_start, range_end + 1))
        # Pre-assign UUIDs
        self.data_points = [DataPoint(id=str(uuid.uuid4()), content=n) for n in self.raw_data]

    def get_data(self):
        return self.data_points

    def _is_prime(self, n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def validate(self, input_data, output):
        # input_data is now the raw content (int) because validation usually runs against the content
        # But wait, main.py will pass the DataPoint.
        # Let's adjust validate to accept ANY, and we handle it.
        
        # If input_data is a DataPoint, extract content.
        if isinstance(input_data, DataPoint):
            val = int(input_data.content)
        else:
            val = int(input_data)
            
        expected = self._is_prime(val)
        
        # Normalize output
        if isinstance(output, str):
            if output.lower() == "true":
                normalized_output = True
            elif output.lower() == "false":
                normalized_output = False
            else:
                return False # Invalid output format is incorrect
        else:
            normalized_output = bool(output)
            
        return normalized_output == expected
