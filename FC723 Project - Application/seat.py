"""
==============================================================================
 seat.py - Aircraft Seat Map Module
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project - Part B

Contains everything related to the physical layout of the Burak757
aircraft: the row/column constants, the aisle and storage positions,
and the functions used to build and validate the in-memory seat map.

This module has no dependency on the database or on booking references
-- it only knows about seats and their basic status ("F" free,
"S" storage, or a booking reference string once reserved). Keeping it
separate makes the aircraft layout easy to test, and easy to reuse if
Apache Airlines later introduces a different aircraft type.
==============================================================================
"""

# ---------------------------------------------------------------------------
# Aircraft layout constants
# ---------------------------------------------------------------------------
TOTAL_ROWS = 80                                    # Rows 1 - 80
SEAT_COLUMNS = ["A", "B", "C", "D", "E", "F"]      # Real seat columns
STORAGE_ROWS = {77, 78}                            # Rows where D & E are storage
STORAGE_COLUMNS = {"D", "E"}                       # Columns affected by storage rows


def build_seat_map():
    """
    Build and return the initial seat map as a dictionary.

    Returns
    -------
    dict[str, str]
        Keys are seat identifiers such as "1A", "45C", "80F".
        Values are "F" (free) or "S" (storage - never bookable).

    Notes
    -----
    The aisle ("X") is a visual/layout marker only. Because it does
    not correspond to a bookable location, it is NOT stored as a
    dictionary entry; it is inserted only when the map is printed
    to the screen.
    """
    seat_map = {}
    for row in range(1, TOTAL_ROWS + 1):
        for col in SEAT_COLUMNS:
            seat_id = f"{row}{col}"
            if row in STORAGE_ROWS and col in STORAGE_COLUMNS:
                seat_map[seat_id] = "S"      # storage - not bookable
            else:
                seat_map[seat_id] = "F"      # free - bookable
    return seat_map


def parse_seat_input(raw_input):
    """
    Validate and normalise a seat identifier typed by the user.

    Parameters
    ----------
    raw_input : str
        Raw text entered by the user, e.g. "12a", " 45C ".

    Returns
    -------
    str or None
        The normalised seat id (e.g. "12A") if the input has a valid
        format (1-80 followed by A-F), otherwise None.
    """
    raw_input = raw_input.strip().upper()
    if len(raw_input) < 2:
        return None

    col = raw_input[-1]
    row_part = raw_input[:-1]

    if col not in SEAT_COLUMNS:
        return None
    if not row_part.isdigit():
        return None

    row = int(row_part)
    if row < 1 or row > TOTAL_ROWS:
        return None

    return f"{row}{col}"


def is_reserved(status):
    """
    Return True if `status` represents a reserved seat.

    A reserved seat no longer stores the letter "R" -- it stores an
    8-character booking reference instead. A seat is therefore
    considered reserved if its status is neither "F" (free), "S"
    (storage) nor "X" (aisle).
    """
    return status not in ("F", "S", "X")


def display_seat_map(seat_map):
    """
    Print a grid of the entire aircraft: columns A-C, aisle (X),
    then D-F, for every row. Any status other than "F"/"S" (i.e. a
    booking reference) is shown as "R" to keep the grid readable.
    """
    print("\n--- Apache Airlines / Burak757 Seat Map ---")
    print("Row  A  B  C  X  D  E  F   (R = booked; use option 5 to look")
    print("                            up the actual booking reference)")
    for row in range(1, TOTAL_ROWS + 1):
        cells = []
        for col in ["A", "B", "C"]:
            status = seat_map[f"{row}{col}"]
            cells.append(status if status in ("F", "S") else "R")
        cells.append("X")
        for col in ["D", "E", "F"]:
            status = seat_map[f"{row}{col}"]
            cells.append(status if status in ("F", "S") else "R")
        row_label = str(row).rjust(3)
        print(f"{row_label}  " + "  ".join(cells))
    print()
