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

# User Manual
This section guides CSPC **Students**, **Faculty**, and **Admins** on how to use the EduROOM Classroom Reservation System.

## 1. Login & User Accounts

### How to Log In
1. Open the EduROOM application.
2. Enter your **CSPC email** and **ID number**.
3. Enter your password and click **Login**.

![EduROOM Login Page](app_screenshots/login-page.png)

## 2. Student User Guide

Students have view-only access. They cannot create reservations.
Their main purpose is to check real-time classroom availability.

### 2.1 Accessing the Classrooms Page

Once logged in, the system automatically opens the Classrooms page.
This page displays all rooms in Academic Building IV, including their availability status.

![Available Classrooms](app_screenshots/available-rooms.png)

### 2.2 View Room Schedule

To see confirmed reservations for a specific classroom, click on the **View Schedule** button of a classroom.

![Classroom Schedule](app_screenshots/room-schedule.png)

### 2.3 Searching for Classrooms

Students can quickly find a room using the built-in search bar. Go to the Search field at the top of the Classrooms page and type keywords related to the room.

![Search Classrooms](app_screenshots/search-rooms.png)

### 2.4 Filtering Rooms

Students can filter classroom results using the **Select Date**, **Start Time**, and **End Time** filters.

![Filter Classrooms](app_screenshots/filter-rooms.png)

## 2.5 Settings & Account Management

### Accessing Settings
1. Click on the settings icon in the top-right corner to open the settings drawer, which displays options for **Profile**, **Dark Mode** , and **Logout**.

![Settings Drawer](app_screenshots/settings-drawer.png)

### View Your Profile
Select **Profile** to view your account details (Name, Email, ID, Role). You can also change your profile picture by clicking **Upload New Picture**.

![Student Profile](app_screenshots/account-profile.png)

### Change Your Password
From your profile page, click **Change Password**, then enter your current password, new password, and confirm the new password before clicking **Update Password**.

![Change Password](app_screenshots/change-password.png)


## 3. Faculty User Guide

Faculty members have access to all student features, plus the ability to **create classroom reservations** and **manage their reservations**.

### 3.1 Viewing Classrooms

Faculty can access the same classroom viewing features as students. But unlike students, faculty members have an **enabled "Reserve" button** for each classroom, allowing them to submit reservation requests.

![Faculty Classrooms View](app_screenshots/faculty-available-rooms.png)

### 3.2 Creating a Reservation

#### Step 1: Navigate to the Classrooms Page
From your dashboard, you will see all available classrooms.

#### Step 2: Select a Classroom
Click on the classroom you want to reserve.

#### Step 3: Fill Out the Reservation Form
Provide the following information: Date, Start Time, End Time, and Purpose of reservation.

![Create Reservation Form](app_screenshots/create-reservation-form.png)

When you select a date, the system automatically displays all **reserved time slots** for that day. You cannot select time periods that are already booked.

#### Step 4: Submit Your Request
Click the **Submit Reservation** button.

#### Step 5: Wait for Admin Approval
Your reservation will be marked as **Pending** until an admin reviews and approves it.

## 3.3 Managing My Reservations
Faculty can view and track all their reservation requests.

### Accessing Your Reservations
1. Click on **My Reservations** from the navigation menu.
2. You will see a list of all your reservation requests organized into two tabs:
   - **Upcoming**: Future reservations you can still manage
   - **Past**: Historical reservation records

![My Reservations Page](app_screenshots/my-reservations.png)

### Managing Upcoming Reservations
You can edit or cancel reservations that are still pending or upcoming. Past reservations cannot be modified

![Edit or Cancel Reservation](app_screenshots/edit-cancel-reservation.png)

### 3.4 Real-Time Notifications

Faculty receive **instant notifications** when their reservations are:
- Approved by an admin
- Rejected by an admin

These updates appear automatically without needing to refresh the page.

![Real-Time Notification](app_screenshots/faculty-notification.png)