"""
==============================================================================
 database.py - SQLite Persistence Module
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project 

Handles all direct interaction with the SQLite database used to store
traveller and booking details. No other module should execute raw SQL
directly -- they should call these functions instead, which keeps the
database schema and queries in one place and makes the rest of the
application easier to test and maintain.

DATABASE SCHEMA
---------------
    CREATE TABLE bookings (
        reference       TEXT PRIMARY KEY,
        passport_number TEXT NOT NULL,
        first_name      TEXT NOT NULL,
        last_name       TEXT NOT NULL,
        seat_row        INTEGER NOT NULL,
        seat_column     TEXT NOT NULL
    );
==============================================================================
"""

import sqlite3

DB_FILE = "bookings.db"


def init_database(db_file=DB_FILE):
    """
    Create the SQLite database file and the 'bookings' table if they
    do not already exist.

    Parameters
    ----------
    db_file : str
        Path to the SQLite database file (defaults to "bookings.db").

    Returns
    -------
    sqlite3.Connection
        An open connection to the database.
    """
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
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
    connection.commit()
    return connection


def save_booking_to_db(connection, reference, passport_number,
                        first_name, last_name, row, column):
    """Insert a new booking row into the database."""
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO bookings
            (reference, passport_number, first_name, last_name,
             seat_row, seat_column)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (reference, passport_number, first_name, last_name, row, column))
    connection.commit()


def delete_booking_from_db(connection, reference):
    """Delete a booking row from the database by its reference."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM bookings WHERE reference = ?", (reference,))
    connection.commit()


def find_booking_by_reference(connection, reference):
    """
    Look up a booking by its reference number.

    Returns
    -------
    tuple or None
        (reference, passport_number, first_name, last_name,
         seat_row, seat_column) if found, otherwise None.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bookings WHERE reference = ?", (reference,))
    return cursor.fetchone()
