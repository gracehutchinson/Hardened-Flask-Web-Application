# Hardened Flask Web Application

A secure Python Flask web application integrating SQLite, AES encryption, and Role-Based Access Control (RBAC) to safely manage user and baking contest data. 

**About this project:** This application was engineered to apply fundamental computer security principles to a basic web platform. It enforces data confidentiality by utilizing external cryptography libraries to protect sensitive user information stored in the SQLite database. Additionally, it implements Role-Based Access Control (RBAC) to restrict user permissions based on assigned security levels, ensuring the Principle of Least Privilege across all endpoints.

## Tech Stack
* **Language:** Python 3
* **Framework:** Flask
* **Database:** SQLite3
* **Libraries:** pycryptodomex (AES Encryption)

## Key Features & Security Implementations
* **Data Confidentiality:** Enforced strict data protection by utilizing custom AES symmetric encryption to securely encrypt sensitive Personally Identifiable Information (Names, Phone Numbers, and Login Passwords) prior to database insertion.
* **Role-Based Access Control (RBAC):** Architected a tiered permission system utilizing signed Flask sessions to map users to specific security levels (1-3). Level 1 users can view personal entries, while Level 2 and 3 users gain escalating administrative access to view user lists and add new authorized accounts.
* **Secure Authentication & Validation:** Implemented strict session-based login and logout functionality. Hardened the application against manipulation by implementing server-side input validation for all contest entries and user creations, ensuring non-empty strings and valid numeric ranges.

## Installation & Setup

1. **Clone the repository and navigate to the project directory:**
   git clone <your-repo-url>
   cd <your-repo-folder>

2. **Create and activate a virtual environment:**
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. **Install dependencies:**
   pip install -r requirements.txt

4. **Set the Flask secret key environment variable:**
   $env:FLASK_SECRET_KEY="<your_secure_generated_key>"

5. **Initialize the database:** 
   python init_db.py
   *Note: This script drops any existing tables and creates fresh user and entry tables with AES-encrypted fields. It also automatically generates three test users (one for each security level) for immediate testing.*

6. **Launch the application:**
   python app.py

The application will be accessible locally at `http://127.0.0.1:5020`.

## Author
Grace Hutchinson
