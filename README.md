# Employee Management System

This project is a Flask-based web application for managing employees, shifts, and attendance logs. It provides an admin interface to add, edit, and delete employee and shift data, along with exporting time logs.

## Features

- **Employee Management**  
  - Add employees to the database.  
  - Edit and delete employee details.  

- **Shift Management**  
  - Add new shifts.  
  - Edit and delete shifts.  

- **Attendance System**  
  - Check-in and check-out functionality for employees.  
  - Automatic calculation of incomplete work hours.  

- **Logs Export**  
  - Export attendance logs within a specific date range as a CSV file.  

## Prerequisites

Before you begin, ensure you have the following installed:  

- **Python** (version 3.8 or higher)  

## Setup and Installation

1. Clone the repository to your local machine (or download as zip from the code drop down):  
   ```bash
   git clone https://github.com/SPCS-Projects/TimeSync
   cd TimeSync

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate  
  
3. Install the required Python packages:
   ```
   pip install -r requirements.txt

## Running the Application  
  
1. Start the Flask server:
   ```
   python app.py

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000

3. In order to access the admin dashboard enter "-1" as the user ID
4. If no admin exists, create one manually in the database
