"""models.py - User classes showing inheritance, encapsulation and polymorphism."""


class User:
    """Base class for all users."""

    def __init__(self, user_id, username, role, campus_id=None):
        # The underscore means "private": other code uses the get methods below
        self._user_id = user_id
        self._username = username
        self._role = role
        self._campus_id = campus_id

    def get_user_id(self):
        return self._user_id

    def get_username(self):
        return self._username

    def get_role(self):
        return self._role

    def get_campus_id(self):
        return self._campus_id

    def tabs(self):
        """Names of the screens this user is allowed to see."""
        return []


class Lecturer(User):
    def __init__(self, user_id, username, campus_id=None):
        User.__init__(self, user_id, username, "Lecturer", campus_id)

    def tabs(self):
        return ["Book Resource", "My Bookings"]


class CampusAdmin(User):
    def __init__(self, user_id, username, campus_id):
        User.__init__(self, user_id, username, "Campus Administrator", campus_id)

    def tabs(self):
        return ["Manage Resources", "Campus Bookings", "Campus Report"]


class SystemOperator(User):
    def __init__(self, user_id, username):
        User.__init__(self, user_id, username, "System Operator")

    def tabs(self):
        return ["All Bookings", "Campus Report", "Comparison Report"]


def create_user(row):
    """Turn a database row into the correct kind of User object."""
    if row["role"] == "Lecturer":
        return Lecturer(row["id"], row["username"], row["campus_id"])
    if row["role"] == "Campus Administrator":
        return CampusAdmin(row["id"], row["username"], row["campus_id"])
    return SystemOperator(row["id"], row["username"])
