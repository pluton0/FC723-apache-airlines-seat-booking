"""
==============================================================================
 reference.py - Booking Reference Generation Module
==============================================================================
Module      : FC723 - Programming Theory
Assignment  : Final Project - Part B, Task B.1

Contains the algorithm used to generate a random, GUARANTEED-UNIQUE
8-character alphanumeric booking reference.

This is kept as a small, standalone function (rather than a class)
because it has no state of its own to manage between calls - it only
needs a Database object to check candidate references against. This
mirrors the Class Diagram (Figure 3 of the Project Report), where
reference generation is shown as a service used by the booking
system rather than an entity with its own persistent state.

ALGORITHM
---------
generate_booking_reference() builds an 8-character string using
random.choices() drawn from the pool of uppercase letters A-Z and
digits 0-9 (36 possible characters per position, so 36^8 ~= 2.8 x 10^12
possible combinations). To make uniqueness a GUARANTEE rather than
just "very likely", every candidate is checked against the bookings
already stored in the database (Database.is_reference_taken()) and,
in the rare case of a collision, discarded in favour of a freshly
generated one. The retry loop is bounded by MAX_ATTEMPTS purely as a
safety net against an almost-full reference space, which will never
realistically occur in this system.
==============================================================================
"""

import random
import string

REFERENCE_LENGTH = 8
REFERENCE_ALPHABET = string.ascii_uppercase + string.digits
MAX_ATTEMPTS = 1000   # safety limit for the uniqueness-retry loop


def generate_booking_reference(db):
    """
    Generate a random, unique 8-character alphanumeric booking reference.

    Steps
    -----
    1. Randomly choose 8 characters from A-Z and 0-9 using
       random.choices() (uniform distribution, with replacement).
    2. Join them into a single 8-character candidate string.
    3. Check the database via db.is_reference_taken(): if the
       candidate already exists, discard it and try again (step 1).
    4. Repeat until a reference that is NOT already in the database
       is produced, or until MAX_ATTEMPTS is reached (safety net).

    Parameters
    ----------
    db : database.Database
        An open Database object, used to verify uniqueness against
        existing bookings.

    Returns
    -------
    str
        A unique 8-character alphanumeric booking reference.

    Raises
    ------
    RuntimeError
        If a unique reference could not be produced after MAX_ATTEMPTS
        tries (would only happen if the reference space were almost
        entirely exhausted, which is not realistic for this system).
    """
    for _ in range(MAX_ATTEMPTS):
        candidate = "".join(random.choices(REFERENCE_ALPHABET, k=REFERENCE_LENGTH))
        if not db.is_reference_taken(candidate):
            return candidate
    raise RuntimeError("Unable to generate a unique booking reference.")
