"""
==============================================================================
 database.py - SQLite (Object-Oriented)
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project - Part B
==============================================================================
"""

import sqlite3


class Database:
    """
    Wraps a single SQLite connection and all operations performed on
    the 'bookings' table.
    """

    DEFAULT_DB_FILE = "bookings.db"

    def __init__(self, db_file=DEFAULT_DB_FILE):
        """Initialize database connection and ensure the bookings table exists."""
        self.db_file = db_file
        self.connection = None
        try:
            # Connect to the local SQLite database file
            self.connection = sqlite3.connect(self.db_file)
            self._create_table()
        except sqlite3.Error as e:
            # REFINEMENT: Safety net if the database file cannot be accessed or created
            print(f"[Database error] Could not open database '{db_file}': {e}")
            print("The program will continue, but bookings cannot be saved.\n")

    def _create_table(self):
        """Create the 'bookings' table if it does not already exist."""
        try:
            cursor = self.connection.cursor()
            # COMPLIANCE: Table structure matches the project brief requirements exactly
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    reference       TEXT PRIMARY KEY,
                    passport_number TEXT NOT NULL,
                    first_name      TEXT NOT NULL,
                    last_name       TEXT NOT NULL,
                    seat_row        INTEGER NOT NULL,
                    seat_column     TEXT NOT NULL
                )
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            # EXCEPTION HANDLING: Prevents the program from crashing if table creation fails
            print(f"[Database error] Could not create 'bookings' table: {e}\n")

    def is_available(self):
        """Helper to check if the database is open before running any queries."""
        return self.connection is not None

    def is_reference_taken(self, reference):
        """Check the database to ensure the newly generated reference is unique."""
        if not self.is_available():
            return False
        try:
            cursor = self.connection.cursor()
            # OPTIMIZATION: Using 'SELECT 1' makes the search much faster than selecting whole rows
            cursor.execute("SELECT 1 FROM bookings WHERE reference = ?", (reference,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            # DEFENSIVE PROGRAMMING: Returns False on error so the main loop doesn't get stuck
            print(f"[Database error] Could not check reference uniqueness: {e}\n")
            return False

    def save_booking(self, reference, passport_number, first_name, last_name, row, column):
        """Insert a verified booking record into the database table."""
        if not self.is_available():
            print("[Database error] No database connection; booking was not saved.\n")
            return False
        try:
            cursor = self.connection.cursor()
            # SECURITY: Using '?' placeholders fully prevents SQL Injection vulnerabilities
            cursor.execute("""
                INSERT INTO bookings
                    (reference, passport_number, first_name, last_name,
                     seat_row, seat_column)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (reference, passport_number, first_name, last_name, row, column))
            self.connection.commit()  # Save changes permanently
            return True
        except sqlite3.Error as e:
            # RELIABILITY: Logs the error but returns False so the program keeps running smoothly
            print(f"[Database error] Could not save booking {reference}: {e}\n")
            return False

    def delete_booking(self, reference):
        """Remove a booking record from the database when a seat is freed."""
        if not self.is_available():
            print("[Database error] No database connection; booking was not deleted.\n")
            return False
        try:
            cursor = self.connection.cursor()
            # REFACTORING: Called by main.py whenever option 3 (Free a seat) is selected
            cursor.execute("DELETE FROM bookings WHERE reference = ?", (reference,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            # DATA INTEGRITY: Failing to delete stops the system from freeing the seat in memory
            print(f"[Database error] Could not delete booking {reference}: {e}\n")
            return False

    def find_booking(self, reference):
        """Search and retrieve booking details using the 8-character reference code."""
        if not self.is_available():
            print("[Database error] No database connection; cannot search bookings.\n")
            return None
        try:
            cursor = self.connection.cursor()
            # READ OPERATION: Fetches the matching row for the Part B lookup feature
            cursor.execute("SELECT * FROM bookings WHERE reference = ?", (reference,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"[Database error] Could not search for booking {reference}: {e}\n")
            return None

    def close(self):
        """Cleanly close the database connection when the program exits."""
        if self.connection is not None:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                print(f"[Database error] Error while closing database: {e}\n")
