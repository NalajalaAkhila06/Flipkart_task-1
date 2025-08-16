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
  git clone https://github.com/malini-30/leave-management-system.git
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
<img width="1600" height="700" alt="Login_Image" src="https://github.com/malini-30/flipkart_project1/blob/main/login.png?raw=true"/>

- ### Admin_Dashboard
<img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/admin_dashboard.png?raw=true"/>

- ### Admin_Profile
<img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/admin_profile.png?raw=true"/>

- ### Admin_Reports
<img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/admin_reports.png?raw=true"/>


- ### Manager Dashboard
<img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/manager_dashboard.png?raw=true" />

- ### Manager Profile
<img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/manager_profile.png?raw=true" />

- ### Manager_Reports
  <img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/manager_reports.png?raw=true"/>

 - ### Employee Dashboard
  <img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/employee_dashboard.png?raw=true"/>

- ### Employee Profile
  <img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/employee_profile.png?raw=true"/>

- ### Employee Leave_Request
    <img width="1600" height="700" alt="Image" src="https://github.com/malini-30/flipkart_project1/blob/main/employee_leave_request.png?raw=true"/>

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
