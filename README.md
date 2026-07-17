# Smart Hospital Management System

A complete, modern, responsive, and professional Hospital Management System built with Python, Streamlit, and a JSON flat-file database.

## Technology Stack
- **Python**: 3.12+
- **Streamlit**: Web interface and application framework
- **Pandas**: Data manipulation and analytics
- **Pillow**: Image management
- **JSON**: Lightweight flat-file storage
- **UUID**: Unique ID generation

## Features
1. **Secure Authentication**: Secure login and register pages with SHA-256 password hashing. Roles: Admin & Doctor.
2. **Dashboard**: High-fidelity SaaS-style metrics dashboard with stats, recent activities, dark/light theme options, and quick search.
3. **Patient Management**: Complete CRUD operations for patient records with filters, details view, and doctor assignment.
4. **Specialists Directory**: Modern profiles for Doctors spanning 13 specializations with search, filter, and scheduling options.
5. **Pharmacy/Tablet Inventory**: Management of medicine stock, expiry dates, dosage, strength, and automatic Low-Stock & Expiry alerts.
6. **Recommendation System**: AI-like rules engine advising tablets, dosages, precautions, and specialist routing based on patient symptoms.
7. **History Log**: Chronological records of issued medicines with CSV export and management tools.
8. **Visual Reports**: Analytical charts (pie, bar, line charts) detailing demographics, specializations, stock status, and medicine consumption.
9. **Settings**: Theme switcher, personal profile configuration, and secure password changes.

## Folder Structure
```
hospital_management_system/
├── app.py                  # Main entry point & routing configuration
├── requirements.txt        # Python package dependencies
├── .env                    # Environment variables
├── README.md               # Documentation
├── assets/                 # App icons & graphics
├── pages/                  # Streamlit page modules
└── utils/                  # Backend utilities (auth, DB, styles, etc.)
└── data/                   # JSON databases
```

## Running the Application Locally

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```
