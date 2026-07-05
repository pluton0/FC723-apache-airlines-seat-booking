"""
==============================================================================
 Apache Airlines - Seat Booking System (PART B - Modular Version)
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project - Part B
Author      : P489993

This is the single executable entry point for the application. It
contains only the menu, the user interaction logic, and the main
program loop. All aircraft layout logic lives in seat.py, all database
access lives in database.py, and the booking reference algorithm lives
in reference.py -- keeping this file focused purely on orchestration.

Run with:
    python main.py

FOLDER STRUCTURE
----------------
    FC723 Project - Application/
        main.py         <- run this file
        seat.py         <- aircraft layout & seat map
        database.py     <- SQLite persistence
        reference.py    <- booking reference algorithm
==============================================================================
"""

from seat import build_seat_map, parse_seat_input, is_reserved, display_seat_map
from database import (
    init_database,
    save_booking_to_db,
    delete_booking_from_db,
    find_booking_by_reference,
)
from reference import generate_booking_reference


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def check_availability(seat_map):
    """Option 1: Check whether a specific seat is available."""
    raw = input("Enter seat to check (e.g. 12A): ")
    seat_id = parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is FREE.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a STORAGE AREA and cannot be booked.\n")
    elif is_reserved(status):
        print(f"Seat {seat_id} is RESERVED (reference: {status}).\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def book_seat(seat_map, connection):
    """
    Option 2: Book a seat.

    On success, a unique booking reference is generated (reference.py)
    and stored in the seat map, and the traveller's details are saved
    to the database (database.py).
    """
    raw = input("Enter seat to book (e.g. 12A): ")
    seat_id = parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "S":
        print(f"Seat {seat_id} is a storage area and cannot be booked.\n")
        return
    if status is None:
        print(f"Seat {seat_id} does not exist.\n")
        return
    if is_reserved(status):
        print(f"Sorry, seat {seat_id} is already reserved.\n")
        return

    passport_number = input("Passport number: ").strip()
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()

    reference = generate_booking_reference(connection)
    row = int("".join(ch for ch in seat_id if ch.isdigit()))
    column = seat_id[-1]

    save_booking_to_db(connection, reference, passport_number,
                        first_name, last_name, row, column)
    seat_map[seat_id] = reference

    print(f"Seat {seat_id} booked successfully. "
          f"Your booking reference is: {reference}\n")


def free_seat(seat_map, connection):
    """
    Option 3: Free a previously booked seat.

    The booking record is also deleted from the database
    (database.py), and the seat map entry is reset to "F".
    """
    raw = input("Enter seat to free (e.g. 12A): ")
    seat_id = parse_seat_input(raw)
    if seat_id is None:
        print(f"'{raw}' is not a valid seat reference.\n")
        return

    status = seat_map.get(seat_id)
    if status == "F":
        print(f"Seat {seat_id} is not currently booked.\n")
    elif status == "S":
        print(f"Seat {seat_id} is a storage area.\n")
    elif is_reserved(status):
        delete_booking_from_db(connection, status)
        seat_map[seat_id] = "F"
        print(f"Seat {seat_id} (reference {status}) has been freed and "
              f"the booking record has been removed from the database.\n")
    else:
        print(f"Seat {seat_id} does not exist.\n")


def search_by_reference(connection):
    """
    Option 5: search for a booking using its reference number and
    display the traveller's details from the database.
    """
    reference = input("Enter booking reference: ").strip().upper()
    result = find_booking_by_reference(connection, reference)
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

    Builds the in-memory seat map (seat.py), opens/creates the SQLite
    database (database.py), then loops over the menu until the user
    exits. The database connection is closed cleanly on exit.
    """
    seat_map = build_seat_map()
    connection = init_database()

    try:
        while True:
            print_menu()
            choice = input("Select an option (1-6): ").strip()

            if choice == "1":
                check_availability(seat_map)
            elif choice == "2":
                book_seat(seat_map, connection)
            elif choice == "3":
                free_seat(seat_map, connection)
            elif choice == "4":
                display_seat_map(seat_map)
            elif choice == "5":
                search_by_reference(connection)
            elif choice == "6":
                print("Thank you for using Apache Airlines Seat Booking System.")
                break
            else:
                print("Invalid option, please choose a number between 1 and 6.\n")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
