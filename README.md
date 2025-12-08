# **EduRoom: Classroom Reservation System**
_A Final Project — Built using Python, Flet, MySQL & WebSockets_

## **Courses Covered**
- CCCS 106 – Application Development and Emerging Technologies
- CS 319 – Information Assurance and Security
- CS 3110 – Software Engineering 1

## **Developed by:** TechValks  
Blessie Faith Bongalos • Ivy Doroin • Renna Israel • Tischia Ann Olivares

**Section:** BSCS 3A 

---

## **Overview**
EduRoom is a cross-platform classroom reservation system designed to streamline room scheduling in Academic Building IV of CSPC.  
It replaces the traditional manual reservation method—paper forms and walk-ins—by offering:

✔ A centralized platform  
✔ Real-time room availability  
✔ Room booking for faculty  
✔ Admin approval dashboard  
✔ Secure authentication and session handling  
✔ Activity logs and analytics  

Built using **Python + Flet** for UI, **MySQL** for data storage, and **WebSockets** for real-time updates.

---

## **Key Features**

### **Baseline Features**
- **User Authentication** (Student, Faculty, Admin)  
- **View Classroom Availability**  
- **Classroom Reservation** (Faculty only)  
- **Admin Approval / Rejection**  
- **Notification System**  
- **Session Management & Inactivity Timeout**
  - Per-session CSRF-style token  
  - Auto-logout after inactivity  
  - Session expiration notice  
  - Activity tracking (`last_activity`)

### **Enhancements**
- **Real-Time Update** via WebSocket server  
- **Clean, responsive UI** with Flet  
- **Profile Management** (update password, view details)  
- **Role-Based Access Control (RBAC)** enforced at UI + server  
- **Admin User Management**
  - Create, update, disable/activate  
  - Reset passwords  
- **Activity Logging** (logins, user changes, approvals)  
- **Secure Configuration** (environment variables)  
- **Analytics Dashboard** (peak hours, usage trends)  
- **Automated Unit Tests**
  - `test_auth.py`  
  - `test_analytics.py`  
  - `test_validation.py`

---

## **System Architecture**

EduRoom follows an **MVC-like structure**:
### **Architecture Layers**
1. **UI Layer** — Flet components & pages  
2. **Application Layer** — Controller logic & validation  
3. **Data Layer** — MySQL queries & models  
4. **Emerging Tech Layer** — WebSocket real-time events  

---

## **Database Model (ERD)**

✔ Users  
✔ Classrooms  
✔ Classroom Images  
✔ Reservations  
✔ Notifications  
✔ Activity Logs  

![ERD Diagram]("C:\Users\Olivares\Downloads\EduROOM_ERD.png")

---

## **Installation & Setup**

### **1. Clone the repository**
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

✔ 108 tests run — all passed
0 failures • 0 errors • 0 skipped

### **Security Highlights**

- bcrypt password hashing
- RBAC for Students / Faculty / Admin
- CSRF-style per-session tokens
- Inactivity timeout & auto-logout
- Validation against SQL injection
- Activity logs for auditing
- Secure .env configuration

### **Analytics & Logs**

**Admins can view:**

- Peak room usage hours
- Approval/rejection rates
- Most frequently used classrooms
- User activity logs

### **Future Enhancements**

- Mobile-friendly UI
- Advanced analytics and reporting
- Login throttling / account lockout
- Predictive room recommendations
- Full WebApp deployment
