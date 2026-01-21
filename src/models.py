import dataclasses
from enum import Enum, auto
from datetime import date
from typing import set, Optional


@dataclasses  
class Staff:
    name: str
    points: int
    unavailDates: set[date]
    biddingDates: set[date]

@dataclasses
class Shift:
    shiftPoints: 1
    shiftDate: date
    assignedStaff: Optional[Staff] = None # If no staff, this defaults to None

     