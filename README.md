# Passport and PAN Card Application Tracker (Dastaavej)

## Description
The Passport and PAN Card Application Tracker, also known as **Dastaavej**, is a web-based platform designed to simplify the process of applying for and tracking passport and PAN card applications.  
- **For Citizens:**  
  - Secure Aadhaar-based login  
  - Real-time status tracking of applications (Pending, Approved, Rejected)  
  - Secure document upload  
  - Timely notifications via email and SMS  

- **For Government Agencies:**  
  - Efficient review of applications  
  - Status updates and management  
  - Ability to provide rejection reasons and additional comments  

This system improves transparency, reduces paperwork, and streamlines the entire process for both citizens and government agencies.

## Motivation
- Simplify and streamline the application process.
- Enhance transparency and reduce manual follow-ups.
- Improve efficiency in managing government document applications.

## Problem Statement
Traditional systems for tracking passport and PAN card applications are complex, lack real-time updates, and require manual follow-ups, causing frustration among citizens and inefficiencies for government agencies.

## Objectives
- Provide real-time application status tracking.
- Enable secure document uploads.
- Ensure efficient review and update of application statuses by government agencies.
- Enhance security with Aadhaar-based authentication and role-based access control (RBAC).

## Proposed Solution (Method / Approach)
- **Backend:** Flask (Python) with RESTful APIs.
- **Database:** PostgreSQL for secure and scalable data management.
- **Authentication:** Aadhaar-based login with JWT for session management.
- **Notifications:** Email and SMS integration for timely updates.
- **Frontend:** HTML, CSS, and JavaScript (using Bootstrap or Tailwind CSS for a responsive design).

## Hardware and Software Requirements

### Hardware
- **Processor:** Minimum Quad-core (Intel i5/AMD Ryzen 5 or higher)
- **RAM:** Minimum 8GB
- **Storage:** Minimum 128GB SSD

### Software
- **IDE:** PyCharm or VS Code
- **Server:** Gunicorn + NGINX for deployment
- **Operating System:** Linux/Windows/macOS
- **Version Control:** Git and GitHub

## Installation Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/dastaavej.git
   cd dastaavej
   ```

2. **Create a Virtual Environment and Install Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup:**
   - Ensure PostgreSQL is installed and running.
   - Create a new database:
     ```bash
     createdb dastaavej_db
     ```
   - Update the database connection details in your configuration file.

4. **Run Database Migrations (if applicable):**
   ```bash
   flask db upgrade
   ```

5. **Start the Server:**
   ```bash
   flask run
   ```

6. **Access the Application:**
   - Open your web browser and go to: `http://localhost:5000`

## Usage
- **Citizens:**  
  - Register or log in using Aadhaar authentication.
  - Upload required documents.
  - Track the status of your application in real-time.
  - Receive notifications about any status updates.

- **Government Agencies:**  
  - Log in via the admin portal.
  - Review submitted applications.
  - Update application statuses and provide feedback or rejection reasons.
  - Monitor overall application management.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License
This project is licensed under the MIT License.

## Contact
For any queries or support, please contact [psumeet08072204@gmail.com].

---

