# EduROOM: Classroom Reservation System  
*A Final Project — Built with Python, Flet, MySQL, and WebSockets*

## Courses Covered
- **CCCS 106** – Application Development and Emerging Technologies  
- **CS 319** – Information Assurance and Security  
- **CS 3110** – Software Engineering 1  

## Developed by: TechValks  
Blessie Faith Bongalos • Ivy Doroin • Renna Israel • Tischia Ann Olivares  
**BSCS 3A — Camarines Sur Polytechnic Colleges**

---

# Project Overview

**EduROOM** is a cross-platform classroom reservation and scheduling system designed for **Academic Building IV of CSPC**.  
It replaces manual reservation workflows with a secure, automated, real-time platform.

The system provides:

- Real-time room availability  
- Faculty reservation submission  
- Administrative approval dashboard  
- User account management  
- Activity logging and analytics  
- Secure authentication and session controls  
- WebSocket-based real-time updates  

Developed using **Python + Flet**, **MySQL**, and **WebSockets**.

---

# Key Features (Aligned with SRS)

## 1. User Authentication & Security
- Secure login using CSPC email + ID  
- Password hashing using **bcrypt**  
- **Login lockout** after 5 failed attempts (10 min window)  
- **Session management & inactivity timeout**  
  - Auto-logout after idle period  
  - Session expiration notice  
  - Activity tracking via `last_activity`  
- **CSRF-style per-session action token**  
- Clean session clearing upon logout  

---

## 2. Role-Based Access Control (RBAC)
| Role | Capabilities |
|------|--------------|
| **Student** | View room availability only |
| **Faculty** | View rooms + submit reservations + view history |
| **Admin** | Approve/reject requests, manage users, manage schedules, view analytics, view logs |

RBAC enforced at both **UI level** and **application logic**.

---

## 3. Reservation Management
- Room search and availability viewing  
- Conflict detection via academic schedules  
- Reservation creation for faculty  
- Admin approval or rejection with remarks  
- Real-time UI updates  
- Reservation history per user  

---

## 4. Real-Time Features (Emerging Tech)
- WebSocket server for push notifications  
- Live updates for:
  - New reservations  
  - Approval/rejection  
  - Analytics refresh  
- Delivery typically < 100 ms  

---

## 5. Profile Management
- View profile information  
- Change password with old-password verification  
- Profile picture support  

---

## 6. Admin User Management
Admins can:  
- Create user accounts  
- Edit user details  
- Change roles  
- Disable/activate accounts  
- Reset passwords  
- Delete accounts  
- View activity logs  
- Access analytics dashboard  

---

## 7. Activity Logging
The system automatically logs critical events:

- Login success/failure  
- Account lockouts  
- User creation, updates, deletions  
- Role changes  
- Password resets  
- Reservation approvals/rejections  

---

## 8. Analytics Dashboard
Admins can view graphical insights:

- Peak classroom usage hours  
- Most frequently used rooms  
- Approval vs rejection metrics  
- Reservation volume over time  

---

# System Architecture

EduROOM follows a modular, layered architecture:

### **1. Presentation Layer**
- Flet UI components  
- Page views and navigation  

### **2. Application Layer**
- Reservation logic  
- User management  
- Session validation  
- Input validation  

### **3. Data Layer**
- MySQL database  
- Model classes for core entities  
- Parameterized SQL queries  

### **4. Realtime Communication Layer**
- WebSocket server for notifications  

### **5. Security Layer**
- Authentication  
- Password hashing  
- Session timeout  
- Action tokens  
- Login lockout  

---

# Database Model (ERD)

The EduROOM database consists of five core entities: **Users**, **Classrooms**, **Reservations**, **Notifications**, and **Activity Logs**.  
Users can create reservations for classrooms, receive notifications about their requests, and generate activity logs based on system actions. Classrooms can have multiple reservations, and each reservation may trigger related notifications. This structure supports secure authentication, room scheduling, and real-time system updates.


*(Insert ERD image in your repo and update the path below)*

![ERD Diagram](assets/erd/EduROOM_ERD.png)

## Installation & Setup

### 1. Clone the repository
```sh
git clone https://github.com/yourusername/EduRoom.git
cd EduRoom

```
### **2. Create & activate virtual environment**
```sh
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux

```
### **3. Install dependencies**
```sh
pip install -r requirements.txt

```
### **4. Import database schema**
  
Import eduroom_schema.sql into MySQL.

### **5. Configure environment variables**

Create a .env file:
```sh
DB_HOST=localhost
DB_USER=root
DB_PASS=yourpassword
DB_NAME=eduroom

```
**Running the Application**
```sh
python main.py

```

The system will launch in a Flet window or your default browser.

**Running Tests**
```sh
python tests/run_tests.py
python tests/test_auth.py
python tests/test_analytics.py
python tests/test_validation.py

```

✔ ALL TESTS PASSED!

# Real-Time WebSocket Setup & Testing

EduROOM uses a dedicated **WebSocket server** to provide real-time updates for:

- New reservation requests  
- Admin approvals and rejections  
- Live analytics dashboard updates  
- User notifications  

This integration fulfills the system’s **Emerging Technology Requirement**.

---

## 1. Start the WebSocket Server

In a separate terminal window, run:

python websocket_server.py


**Expected output:**
WebSocket server started on ws://localhost:8765
Waiting for clients...


> The WebSocket server must remain running for real-time updates to function properly.

---

## 2. Launch the Main Application

Open another terminal window and run:

python main.py


**When the client connects successfully, the WebSocket server displays:**
Client connected: 127.0.0.1


---

## 3. Testing Real-Time Features

### ✔ Test A — New Reservation Appears Instantly on Admin Dashboard

1. Log in as **Faculty**.  
2. Submit a new reservation request.  
3. Log in as **Admin** in another application window.  
4. The new request should appear instantly (within <100 ms) **without refreshing**.

**WebSocket server output:**
Broadcasting message: new_reservation


**Admin client output:**
Received message: new_reservation

---

### ✔ Test B — Admin Approval/Rejection Notifies Faculty Immediately

1. Admin approves or rejects the reservation.  
2. Faculty receives a **real-time notification** in the UI.

**WebSocket server output:**
Broadcasting message: reservation_update

**Faculty client output:**
Received message: reservation_update


---

### ✔ Test C — Analytics Dashboard Auto-Refresh

1. Open the **Analytics Dashboard** as Admin.  
2. Trigger reservation changes from a Faculty account.  
3. The analytics dashboard automatically refreshes **without reloading** the page.

---

## 4. Expected Performance

| Metric | Target Performance |
|--------|--------------------|
| Local WebSocket message delay | 10–50 ms |
| Guaranteed max delay | <500 ms |

EduROOM’s WebSocket system ensures **true real-time responsiveness**, meeting all **SRS performance requirements**.

---

## 5. Troubleshooting

| Issue | Solution |
|-------|-----------|
| No real-time updates | Ensure `websocket_server.py` is running |
| Connection refused | Check that port `8765` is free |
| No client connection | Verify the WebSocket URL: `ws://localhost:8765` |
| Updates delayed | Restart both the WebSocket server and the app |
| Two users not syncing | Restart each app window to reconnect clients |

---

**© EduROOM Project 2025**
