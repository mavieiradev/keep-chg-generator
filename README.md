# QD Apps - Support (Change Management System)

<div align="center">
    <img src="https://spread.com.br/wp-content/uploads/2023/10/logo-white.svg" width="250">
</div>

## 📋 Description

QD Apps - Support is a system developed to assist support teams in managing and controlling CHGs (Change Management). This tool automates the process of generating reports for communicating planned changes, facilitating the monitoring and notification of stakeholders through the Keep application.

## ✨ Features

- **Keep CHGs Generator**: Automatically creates formatted reports for Keep based on CHG files
- **Smart Filter**: Identifies relevant CHGs for the current period (today from 5:00 PM and tomorrow until 4:00 AM)
- **Preview**: Allows you to preview the report before downloading it
- **Test Processing**: Handles and analyzes test data from different platforms
- **Occurrence Updates**: Integrates functional and critical occurrence data

## 🚀 Technologies Used

- **Streamlit**: Framework for creating the web interface
- **Pandas**: Data processing and analysis
- **OpenPyXL**: Advanced Excel file manipulation
- **Python Timezone (pytz)**: Timezone management
- **PIL (Pillow)**: Image processing

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/your-user/qd-apps-support.git

# Enter the directory
cd qd-apps-support

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run generate_chg_report.py
```

## 📊 How to Use

1. Start the application with `streamlit run generate_chg_report.py`
2. Access the application in the browser (usually at http://localhost:8501)
3. In the "Keep CHGs Generator" tab, upload the Excel file containing the CHGs
4. The system will automatically process the file and generate a formatted report
5. Preview and download the report

## 📁 Project Structure

- **generate_chg_report.py**: Main file containing the application logic
- **logger.py**: Logging configuration and functions
- **chg_comparator.py**: Module for comparing CHGs
- **spread_logo.png**: Logo used in the interface
- **requirements.txt**: Project dependencies

## 🔄 Processing Flow

1. The user uploads an Excel file containing CHG information
2. The system filters relevant CHGs (today from 5:00 PM and tomorrow until 4:00 AM)
3. The filtered CHGs are formatted into a report for Keep
4. The user can preview and download the generated report

## 👥 Developed by

QD Apps Support Team - Spread

## 📄 License

Proprietary - © 2025 Spread

---

*Version 2.5*
