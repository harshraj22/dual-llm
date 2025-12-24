from abc import ABC, abstractmethod
from typing import Any, List, Tuple
from dataclasses import dataclass
import uuid

@dataclass
class DataPoint:
    id: str
    content: Any

class BaseDataset(ABC):
    @abstractmethod
    def get_data(self) -> List[DataPoint]:
        """Returns a list of DataPoint objects."""
        pass

    @abstractmethod
    def get_instruction(self) -> str:
        """Returns the evaluation instruction/rule for this dataset."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Returns the number of data points."""
        pass

    @abstractmethod
    def __getitem__(self, idx) -> DataPoint:
        """Returns a specific data point by index."""
        pass

    @abstractmethod
    def validate(self, input_data: Any, output: Any) -> bool:
        """Returns True if the output is correct for the input_data."""
        pass
