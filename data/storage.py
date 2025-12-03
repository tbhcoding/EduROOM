# Temporary in-memory storage (will be replaced with database later)

USERS = {
    # Admin account
    "admin": {
        "password": "admin123", 
        "role": "admin", 
        "name": "Admin User",
        "email": "admin@cspc.edu.ph",
        "id_number": "00000000"
    },
    # Faculty accounts
    "faculty1": {
        "password": "faculty123", 
        "role": "faculty", 
        "name": "Prof. Smith",
        "email": "profsmith@my.cspc.edu.ph",
        "id_number": "20231001"
    },
    "faculty2": {
        "password": "faculty123", 
        "role": "faculty", 
        "name": "Prof. Johnson",
        "email": "profjohnson@my.cspc.edu.ph",
        "id_number": "20231002"
    },
    # Student accounts
    "student1": {
        "password": "student123", 
        "role": "student", 
        "name": "John Doe",
        "email": "johndoe@my.cspc.edu.ph",
        "id_number": "25123456"
    },
    "student2": {
        "password": "student123", 
        "role": "student", 
        "name": "Jane Smith",
        "email": "janesmith@my.cspc.edu.ph",
        "id_number": "25123457"
    }
}

CLASSROOMS = [
    {"id": 1, "name": "Room 101", "capacity": 30, "building": "Main Building", "status": "Available"},
    {"id": 2, "name": "Room 102", "capacity": 25, "building": "Main Building", "status": "Available"},
    {"id": 3, "name": "Lab 201", "capacity": 20, "building": "Science Building", "status": "Available"},
    {"id": 4, "name": "Room 301", "capacity": 35, "building": "Main Building", "status": "Available"},
    {"id": 5, "name": "Lab 202", "capacity": 15, "building": "Science Building", "status": "Available"},
]

RESERVATIONS = []

def get_user(username):
    """Get user by username"""
    return USERS.get(username)

def get_user_by_id_number(id_number):
    """Get user by ID number"""
    for username, user_data in USERS.items():
        if user_data.get("id_number") == id_number:
            return username, user_data
    return None, None

def get_user_by_email(email):
    """Get user by email"""
    for username, user_data in USERS.items():
        if user_data.get("email") == email:
            return username, user_data
    return None, None

def authenticate_user(id_number, password):
    """Authenticate user by ID number and password"""
    username, user_data = get_user_by_id_number(id_number)
    if user_data and user_data["password"] == password:
        return username, user_data
    return None, None

def get_classroom(classroom_id):
    """Get classroom by ID"""
    return next((r for r in CLASSROOMS if r["id"] == classroom_id), None)

def add_reservation(classroom_name, username, date, start_time, end_time, purpose):
    """Add a new reservation (pending approval)"""
    reservation = {
        "id": len(RESERVATIONS) + 1,
        "classroom": classroom_name,
        "user": username,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": purpose,
        "status": "pending"  # All reservations start as pending
    }
    RESERVATIONS.append(reservation)
    return reservation

def get_user_reservations(username):
    """Get all reservations for a specific user"""
    return [r for r in RESERVATIONS if r["user"] == username]

def get_all_reservations():
    """Get all reservations (for admin)"""
    return RESERVATIONS

def get_pending_reservations():
    """Get all pending reservations (for admin approval)"""
    return [r for r in RESERVATIONS if r["status"] == "pending"]

def approve_reservation(reservation_id):
    """Approve a reservation"""
    for r in RESERVATIONS:
        if r["id"] == reservation_id:
            r["status"] = "approved"
            return True
    return False

def reject_reservation(reservation_id):
    """Reject a reservation"""
    for r in RESERVATIONS:
        if r["id"] == reservation_id:
            r["status"] = "rejected"
            return True
    return False