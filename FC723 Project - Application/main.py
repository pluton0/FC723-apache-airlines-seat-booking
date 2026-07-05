"""
==============================================================================
 Apache Airlines - Seat Booking System (PART B - Modular, OOP Version)
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project - Part B
==============================================================================
"""

import sqlite3

from seat import SeatMap
from database import Database
from reference import generate_booking_reference


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def check_availability(seat_map):
    """Option 1: Check whether a specific seat is available."""
    raw = input("Enter seat to check (e.g. 12A): ")
    # VALIDATION: Delegate formatting checking to the static helper in SeatMap
    seat_id = SeatMap.parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    # COUPLING: Query the SeatMap state without accessing the underlying dictionary directly
    status = seat_map.get_status(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is FREE.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a STORAGE AREA and cannot be booked.\n")
    elif SeatMap.is_reserved(status):
        print(f"Seat {seat_id} is RESERVED (reference: {status}).\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def book_seat(seat_map, db):
    """
    Option 2: Book a seat.

    On success, a unique booking reference is generated (reference.py)
    and stored in the seat map, and the traveller's details are saved
    to the database via the Database object. All database access goes
    through Database's own try/except handling, so a database failure
    here is reported to the user rather than crashing the program.
    """
    raw = input("Enter seat to book (e.g. 12A): ")
    seat_id = SeatMap.parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    # DEFENSIVE PROGRAMMING: Verify layout constraints before asking for passenger info
    status = seat_map.get_status(seat_id)
    if status == "S":
        print(f"Seat {seat_id} is a storage area and cannot be booked.\n")
        return
    if status is None:
        print(f"Seat {seat_id} does not exist.\n")
        return
    if SeatMap.is_reserved(status):
        print(f"Sorry, seat {seat_id} is already reserved.\n")
        return

    passport_number = input("Passport number: ").strip()
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()

    # ALGORITHMIC DEPENDENCY: Pass the Database object as a service to ensure uniqueness
    try:
        reference = generate_booking_reference(db)
    except RuntimeError as e:
        print(f"[Booking error] Could not generate a booking reference: {e}\n")
        return

    # DATA CONVERSION: Extract structural values matching the database table schema
    row = int("".join(ch for ch in seat_id if ch.isdigit()))
    column = seat_id[-1]

    # TRANSACTION VALIDATION: Only update the in-memory map if the persistent database write succeeds
    saved = db.save_booking(reference, passport_number, first_name, last_name, row, column)
    if not saved:
        print(f"Seat {seat_id} could not be booked due to a database error. "
              f"Please try again.\n")
        return

    seat_map.set_status(seat_id, reference)
    print(f"Seat {seat_id} booked successfully. "
          f"Your booking reference is: {reference}\n")


def free_seat(seat_map, db):
    """
    Option 3: Free a previously booked seat.

    The booking record is also deleted from the database, and the
    seat map entry is reset to "F" only if the delete succeeds -
    this avoids a seat becoming falsely "free" in memory while its
    booking record still lingers in the database after a failed delete.
    """
    raw = input("Enter seat to free (e.g. 12A): ")
    seat_id = SeatMap.parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get_status(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is not currently booked.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a storage area.\n")
    elif SeatMap.is_reserved(status):
        # DATA CONSISTENCY: Ensure memory layout and SQL database stay completely synchronized
        deleted = db.delete_booking(status)
        if deleted:
            seat_map.set_status(seat_id, "F")
            print(f"Seat {seat_id} (reference {status}) has been freed and "
                  f"the booking record has been removed from the database.\n")
        else:
            print(f"Seat {seat_id} could not be freed due to a database error. "
                  f"Please try again.\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def search_by_reference(db):
    """Option 5: Search for a booking using its reference number."""
    reference = input("Enter booking reference: ").strip().upper()
    # ENCAPSULATION: Query execution logic is fully contained inside the Database class
    result = db.find_booking(reference)
    if result is None:
        print(f"No booking found with reference {reference}.\n")
        return

    ref, passport_number, first_name, last_name, row, column = result
    print(f"\nBooking found: {ref}")
    print(f"  Passenger : {first_name} {last_name}")
    print(f"  Passport  : {passport_number}")
    print(f"  Seat      : {row}{column}\n")


def print_menu():
    """Display the main menu options to the user."""
    print("=" * 50)
    print(" APACHE AIRLINES - SEAT BOOKING SYSTEM (Part B)")
    print("=" * 50)
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Search booking by reference")
    print("6. Exit program")
    print("=" * 50)


def main():
    """
    Main program loop.

    Creates one SeatMap object (in-memory aircraft layout) and one
    Database object (SQLite persistence), then loops over the menu
    until the user exits. The database connection is closed cleanly
    on exit regardless of how the loop ends.
    """
    # COMPLIANCE: Instantiate classes reflecting the associations in the UML Class Diagram
    seat_map = SeatMap()
    db = Database()

    try:
        # PERSISTENT CONTROL FLOW: Keep the application running inside a continuous loop
        while True:
            print_menu()
            choice = input("Select an option (1-6): ").strip()

            try:
                if choice == "1":
                    check_availability(seat_map)
                elif choice == "2":
                    book_seat(seat_map, db)
                elif choice == "3":
                    free_seat(seat_map, db)
                elif choice == "4":
                    seat_map.display()
                elif choice == "5":
                    search_by_reference(db)
                elif choice == "6":
                    print("Thank you for using Apache Airlines Seat Booking System.")
                    break
                else:
                    print("Invalid option, please choose a number between 1 and 6.\n")
            except sqlite3.Error as e:
                # RELIABILITY: Catch all block for unhandled low level database engine errors
                print(f"[Unexpected database error] {e}\n"
                      f"Please try that action again.\n")
    finally:
        # RESOURCE MANAGEMENT: Guarantee the file handle is closed even if the program terminates unexpectedly
        db.close()


if __name__ == "__main__":
    main()
