# Leave Management System
>  Built by **Nalajala Akhila** for Flipkart Task-1  
> 🗓 Last Updated: **10 August 2025**

A comprehensive web-based Leave Management System built with Flask, SQLAlchemy, and modern HTML/CSS.

## Overview
-
The Employee Leave Management System (ELMS) is a comprehensive web application designed to streamline and automate the process of managing employee leave requests. It provides features for employees to request leave, managers to approve/reject requests, and administrators to manage the system and generate reports.
---


## Features
- **User Authentication**: Secure login for employees, managers, and administrators
- **User Roles:** Admin, Manager, and Employee with different permissions

- **Leave Request Workflow:** Submit, approve, reject, and cancel leave requests

- **Dashboard:** Overview of leave statistics and recent requests

- **Reporting:** Generate CSV and PDF reports

- **User Management:** Admin can create and manage users

- **Profile Management:** Users can update their profiles and change passwords

- **Responsive Design:** Works on desktop and mobile devices

---
## Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python, Flask
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Reporting:** CSV, PDF generation

## Installation
1. Clone the repository:
   ```bash
  git clone https://github.com/NalajalaAkhila06/Flipkart_task-1.git
cd leave-management-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
  ```bash
      python app.py
```
5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application at :```http://localhost:127.0.0.1:5000```

---

## Default Users

The system creates default users when first initialized:

- Admin:

      Username: admin
      Password: admin123

- Manager:
  
      Username: manager
      Password: mng123

- Employee:
  
      Username: employee
      Password: employee123

---

## Project Structure

```bash
leave-management-system/
├── app.py                 # Main application file
├── templates/             # HTML templates
│   ├── _flash_messages.html
│   ├── _leave_status_badge.html
│   ├── _pagination.html
│   ├── 404.html
│   ├── 500.html
│   ├── base.html
│   ├── change_password.html
│   ├── dashboard.html
│   ├── leave_requests.html
│   ├── login.html
│   ├── new_leave_request.html
│   ├── new_user.html
│   ├── profile.html
│   ├── reports.html
│   ├── users.html
│   └── view_leave_request.html
├── README.md              # This file
└── requirements.txt       # Python dependencies

```
---

## Individual Features 


### Employee Features
- View leave balances
- Submit new leave requests
- Track request status
- View request history

### Manager Features
- Approve/reject leave requests
- View team leave calendar
- Monitor pending approvals

### Admin Features
- Manage all users
- Configure leave types
- Generate system reports
- Monitor system activity
---
## Screenshots

- ### Login Page
<img width="1898" height="940" alt="Screenshot 2025-08-16 220609" src="https://github.com/user-attachments/assets/75426ffd-8d03-424b-b31e-0f5014735b2b" />


- ### Admin_Dashboard
<img width="1912" height="939" alt="Screenshot 2025-08-16 222659" src="https://github.com/user-attachments/assets/72e12853-3413-4bd7-bba3-ad9048ece2c3" />

- ### Admin_Profile

<img width="1319" height="640" alt="Screenshot 2025-08-16 223318" src="https://github.com/user-attachments/assets/4ec73697-4a84-4296-b545-09ca56218896" />

- ### Admin_Reports
<img width="1910" height="899" alt="Screenshot 2025-08-16 223454" src="https://github.com/user-attachments/assets/0ede6c42-efc6-4092-867e-2e0055985c8a" />

 ### Admin Quick reports
 <img width="1916" height="931" alt="Screenshot 2025-08-16 223629" src="https://github.com/user-attachments/assets/7ce1cd3c-83dd-4f38-87ab-566ca75dee0c" />

### Total Users details
<img width="1916" height="951" alt="Screenshot 2025-08-16 223834" src="https://github.com/user-attachments/assets/dd4be520-8548-4c53-a185-e9764883e4df" />

### Admin logout
<img width="1903" height="943" alt="Screenshot 2025-08-16 224107" src="https://github.com/user-attachments/assets/392f9c19-dd49-443a-b3a1-2fb7ce27bfda" />

### Admin logged  out
<img width="1889" height="899" alt="Screenshot 2025-08-16 224514" src="https://github.com/user-attachments/assets/c835e336-c694-4fbf-a516-017e23b4e7af" />

- ### Manager Dashboard
<img width="1913" height="902" alt="Screenshot 2025-08-16 224929" src="https://github.com/user-attachments/assets/bdc41458-54f4-4ef3-966e-4b845f1abaae" />

- ### Manager Profile
<img width="1916" height="895" alt="Screenshot 2025-08-16 225055" src="https://github.com/user-attachments/assets/6d3c28f6-94ec-419c-b75f-39e71538e239" />


- ### Manager_Reports
 <img width="939" height="461" alt="image" src="https://github.com/user-attachments/assets/3f46d9fc-bbb9-45fe-a3e1-aeaad362f5f1" />

### Manager Approved leave
<img width="953" height="466" alt="image" src="https://github.com/user-attachments/assets/f0673aa5-8183-423f-bbb1-a0c540ce5245" />

### Manager notifications
<img width="1866" height="695" alt="Screenshot 2025-08-16 225353" src="https://github.com/user-attachments/assets/c052ee0b-7c64-4d5a-b3db-06d110eaefab" />

### Manager  profile updated and logout
<img width="1885" height="894" alt="Screenshot 2025-08-16 225454" src="https://github.com/user-attachments/assets/f2f1962a-a159-40d9-bad1-dcb6b7566f51" />


 - ### Employee Dashboard
  <img width="1895" height="889" alt="Screenshot 2025-08-16 224608" src="https://github.com/user-attachments/assets/268fe733-866f-4039-a8bb-ff25afc0f09d" />

- ### Employee Profile
 <img width="1919" height="899" alt="Screenshot 2025-08-16 224757" src="https://github.com/user-attachments/assets/f4b7e86e-0838-414c-be6a-cbc3db2701ed" />

- ### Employee Leave_Request
    <img width="959" height="450" alt="image" src="https://github.com/user-attachments/assets/cd4f943d-e30d-4be8-9860-2f569dc96ce1" />

### Employee logout
<img width="951" height="473" alt="image" src="https://github.com/user-attachments/assets/a1b8cf03-32a6-46ff-bc8f-d6623521ea05" />

    -----

## Database Schema
The system uses the following database tables:
- `User`: Stores employee information
- `LeaveType`: Defines different types of leave
- `LeaveRequest`: Tracks all leave requests
- `LeaveBalance`: Maintains leave balances for employees

---

## Future Enhancements:
- Email notifications for leave request status changes
- Calender view of approved leaves
- Leave balance tracking
- Multi-language support
- API endpoints for mobile applications

--- 

## Acknowledgements
- Flask documentation
- Font Awesome for icons
- Various open source projects that inspired this work

---
## License
This project is licensed under the MIT License. See the LICENSE file for details.

---
## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---
## Contact
For questions or support, please contact the project maintainer at nalajalaakhila@gmail.com
