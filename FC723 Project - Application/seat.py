"""
==============================================================================
 seat.py - Aircraft Seat Map Module (Object-Oriented)
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project - Part B
==============================================================================
"""


class SeatMap:
    """
    Represents the seat layout of a single Burak757 aircraft.

    Attributes
    ----------
    grid : dict[str, str]
        Maps a seat identifier (e.g. "12A") to its current status:
        "F" (free), "S" (storage - never bookable), or an 8-character
        booking reference string if the seat is reserved.
    """

    TOTAL_ROWS = 80                                    # Rows 1 - 80
    SEAT_COLUMNS = ["A", "B", "C", "D", "E", "F"]      # Real seat columns
    STORAGE_ROWS = {77, 78}                            # Rows where D & E are storage
    STORAGE_COLUMNS = {"D", "E", "F"}                       # Columns affected by storage rows

    def __init__(self):
        """Build the initial seat map when a SeatMap object is created."""
        # STATE ENCAPSULATION: Instantiate the core collection immediately upon object creation
        self.grid = self._build_seat_map()

    def _build_seat_map(self):
        """Build and return the initial seat map as a dictionary."""
        grid = {}
        for row in range(1, self.TOTAL_ROWS + 1):
            for col in self.SEAT_COLUMNS:
                seat_id = f"{row}{col}"
                # CONDITIONAL LAYOUT: Enforce physical aircraft storage boundary rules 
                if row in self.STORAGE_ROWS and col in self.STORAGE_COLUMNS:
                    grid[seat_id] = "S"      # storage - not bookable 
                else:
                    grid[seat_id] = "F"      # free - bookable 
        return grid

    @staticmethod
    def parse_seat_input(raw_input):
        """Validate and normalise a seat identifier typed by the user."""
        # INPUT STANDARDISATION: Strip whitespaces and force uniform case matching
        raw_input = raw_input.strip().upper()
        if len(raw_input) < 2:
            return None

        col = raw_input[-1]
        row_part = raw_input[:-1]

        # STRUCTURAL CHECK: Verify row/column components map to valid plane coordinates
        if col not in SeatMap.SEAT_COLUMNS:
            return None
        if not row_part.isdigit():
            return None

        row = int(row_part)
        if row < 1 or row > SeatMap.TOTAL_ROWS:
            return None

        return f"{row}{col}"

    @staticmethod
    def is_reserved(status):
        """Return True if `status` represents a reserved seat."""
        # BUSINESS LOGIC: A seat is reserved if it holds a unique alphanumeric reference 
        return status not in ("F", "S", "X")

    def get_status(self, seat_id):
        """Return the current status of a seat, or None if it does not exist."""
        # DATA ABSTRACTON: Expose status safely without exposing the underlying dict directly
        return self.grid.get(seat_id)

    def set_status(self, seat_id, status):
        """Set the status of a seat (e.g. to a booking reference or back to 'F')."""
        # STATE MUTATION: Explicit method to modify state, ensuring clean integration with main.py
        self.grid[seat_id] = status

    def display(self):
        """Print a grid of the entire aircraft."""
        print("\n--- Apache Airlines / Burak757 Seat Map ---")
        print("Row  A  B  C  X  D  E  F   (R = booked; use option 5 to look")
        print("                            up the actual booking reference)")
        for row in range(1, self.TOTAL_ROWS + 1):
            cells = []
            # UI SEPARATION: Columns A-C rendered before the physical aisle path 
            for col in ["A", "B", "C"]:
                status = self.grid[f"{row}{col}"]
                cells.append(status if status in ("F", "S") else "R")
            
            cells.append("X")  # DYNAMIC RENDERING: Inject aisle marker without storing it in memory 
            
            # UI SEPARATION: Columns D-F rendered after the aisle path 
            for col in ["D", "E", "F"]:
                status = self.grid[f"{row}{col}"]
                cells.append(status if status in ("F", "S") else "R")
            
            # ALIGNMENT: Pad row indices to guarantee perfectly aligned grid formatting
            row_label = str(row).rjust(3)
            print(f"{row_label}  " + "  ".join(cells))
        print()
