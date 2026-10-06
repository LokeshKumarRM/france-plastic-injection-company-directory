# 🇫🇷 France Plastic Injection Company Directory

An end-to-end **web scraping and data analytics project** that collects, cleans, validates, enriches, and organizes information about plastic injection companies in France.

The project transforms publicly available company information into a structured and searchable business directory using **Python, Pandas, SQL Server, Excel, and Power BI**.

---

## 📌 Project Overview

The objective of this project was to build a structured directory of **plastic injection companies in France** from publicly available information.

The project follows an end-to-end data workflow:

```text
Public Web Source
       ↓
Python Web Scraping
       ↓
Data Cleaning
       ↓
Data Validation
       ↓
Geographic Enrichment
       ↓
Excel Company Directory
       ↓
SQL Server Database
       ↓
Power BI Analytics


The project demonstrates how raw web data can be transformed into a clean, validated, structured, and searchable business dataset.


📊 Dataset Overview
The final dataset contains 120 company records.
Metric	Count
Total Companies	120
Companies with Website	103
Companies with Phone	119
Companies with Postal Code	119
Companies with Department	118
Companies with Region	118


📋 Data Fields
The final dataset contains the following information:
- Company Name
- Address
- City
- Postal Code
- Country
- Phone
- Website
- Department Code
- Department
- Region Code
- Region
- Source URL
- Geographic Match Status
🛠️ Technologies Used
Programming & Data Processing
- Python
- Pandas
- Requests
- BeautifulSoup
- OpenPyXL
Database
- Microsoft SQL Server
- SQL
- pyodbc
Analytics & Reporting
- Microsoft Excel
- Power BI
Development Tools
- Visual Studio Code
- Git
- GitHub
🔎 1. Web Scraping
The project starts by collecting company information from a public French business directory.
Python Requests is used to retrieve the webpage, while BeautifulSoup is used to parse the HTML content.
The scraper collects information such as:
- Company name
- Address
- City
- Postal code
- Phone number
- Website
- Source URL
The scraper successfully collected 120 company records.
Script
scraper.py

🧹 2. Data Cleaning
The raw scraped data is cleaned and standardized using Pandas.
The cleaning process includes:
- Cleaning company names
- Standardizing phone numbers
- Cleaning website URLs
- Preserving postal codes as text
- Handling missing values
- Standardizing country values
- Removing duplicate records
- Standardizing source numbers
Cleaning Result
Raw records:          120
Duplicates removed:    0
Final records:        120

Script
clean_data.py

✅ 3. Data Validation
After cleaning, the dataset is validated to ensure that the final records are consistent and usable.
The validation process checks:
- Duplicate records
- Duplicate company names
- Postal code validity
- Phone number validity
- Website URL validity
- Missing values
- Source number consistency
- LinkedIn administrative URLs
Validation Result
Records loaded:       120
Duplicate records:      0
Duplicate names:        0
Invalid postal codes:   0
Invalid phones:         0
Invalid websites:      0

Script
validate_data.py

🌍 4. Geographic Enrichment
The company dataset is enriched with French geographic information.
The enrichment process uses the French government geographic API to identify:
- Department
- Department Code
- Region
- Region Code
The matching process uses available postal code and city information.
The project avoids guessing geographic information when a reliable match cannot be established.
Enrichment Result
Total records:          120
Matched by city:        117
Matched by postal code:   1
Missing postal code:      1
Not found:                1

Script
geographic_enrichment.py

📗 5. Excel Company Directory
The enriched dataset is exported into a practical Excel company directory.
The Excel directory provides:
- Searchable company records
- Excel filters
- Sortable columns
- Clickable website links
- Clickable source links
- Company location information
- Department information
- Region information
This makes it easy to search for a company and quickly access its available business information.
Output File
data/
└── France_Plastic_Injection_Company_Directory.xlsx

🗄️ 6. SQL Server Database
The final dataset is imported into Microsoft SQL Server for structured storage and analysis.
Database
FrancePlasticInjectionDB

Table
PlasticInjectionCompanies

The SQL Server table contains all 120 company records.
Database Columns
CompanyID
SourceNo
CompanyName
Address
City
PostalCode
DepartmentCode
Department
RegionCode
Region
Country
Phone
Website
SourceURL
GeoMatchStatus

Script
sql_import.py

📈 7. SQL Analysis
SQL queries are used to analyze the company directory.
Companies by Region
SELECT
    Region,
    COUNT(*) AS CompanyCount
FROM PlasticInjectionCompanies
GROUP BY Region
ORDER BY CompanyCount DESC;

Companies by Department
SELECT
    Department,
    COUNT(*) AS CompanyCount
FROM PlasticInjectionCompanies
GROUP BY Department
ORDER BY CompanyCount DESC;

Companies Without Websites
SELECT
    CompanyName,
    City,
    Phone
FROM PlasticInjectionCompanies
WHERE Website IS NULL
   OR Website = '';

Companies Without Phone Numbers
SELECT
    CompanyName,
    City,
    Website
FROM PlasticInjectionCompanies
WHERE Phone IS NULL
   OR Phone = '';

These queries can be used to understand company distribution and identify incomplete business information.


📊 8. Power BI
The SQL Server database can be connected to Power BI for interactive data analysis and reporting.
The dataset can be used to create visualizations such as:
- Companies by Region
- Companies by Department
- Website Availability
- Geographic Distribution
- Company Directory
- Company filtering by location
Power BI provides an interactive reporting layer on top of the structured SQL Server database.


📁 Project Structure
france-plastic-injection-company-directory/
│
├── data/
│   ├── france_plastic_injection_companies_final.csv
│   └── France_Plastic_Injection_Company_Directory.xlsx
│
├── scraper.py
├── clean_data.py
├── validate_data.py
├── geographic_enrichment.py
├── create_excel.py
├── sql_import.py
│
├── requirements.txt
├── README.md
└── .gitignore

🔄 End-to-End Workflow
Step 1 — Scrape
Collect company information from the public source using Python.
Step 2 — Clean
Clean and standardize the raw data using Pandas.
Step 3 — Validate
Check the dataset for duplicates, invalid values, and missing information.
Step 4 — Enrich
Add department and region information using geographic data.
Step 5 — Export
Create CSV and Excel outputs.
Step 6 — Store
Import the final dataset into SQL Server.
Step 7 — Analyze
Use SQL queries to analyze the structured dataset.
Step 8 — Visualize
Connect the SQL Server database to Power BI for interactive reporting.
📦 Installation
Clone the repository:
git clone https://github.com/YOUR_USERNAME/france-plastic-injection-company-directory.git

Navigate to the project directory:
cd france-plastic-injection-company-directory

Install the required Python packages:
pip install -r requirements.txt

▶️ Running the Project
Run the scripts in the following order:
1. Scrape the data
python scraper.py

2. Clean the data
python clean_data.py

3. Validate the data
python validate_data.py

4. Enrich geographic information
python geographic_enrichment.py

5. Create the Excel directory
python create_excel.py

6. Import the dataset into SQL Server
python sql_import.py

🎯 Project Objectives
This project demonstrates practical skills in:
- Web Scraping
- Data Collection
- Data Cleaning
- Data Validation
- Data Transformation
- Geographic Data Enrichment
- Excel Data Organization
- SQL Server
- SQL Analysis
- Python
- Pandas
- Power BI
- Business Intelligence
- End-to-End Data Workflows


💡 Key Takeaway
This project demonstrates how raw public web data can be transformed into a structured business dataset through a complete data pipeline.
The workflow combines:
Web Scraping
      +
Python
      +
Pandas
      +
Data Cleaning
      +
Data Validation
      +
Geographic Enrichment
      +
SQL Server
      +
Excel
      +
Power BI



The final result is a searchable directory containing 120 plastic injection companies in France, with company, contact, location, department, and regional information.



⚠️ Data Disclaimer
This project uses information collected from a publicly available source for educational, portfolio, and data-analysis purposes.
Company information may change over time. Important business information should be verified directly with the respective company or original source.


👨‍💻 Author
Lokesh Kumar R M
Aspiring Data Analyst
Skills
Python Pandas SQL SQL Server Power BI Excel Web Scraping Data Cleaning Data Analysis
```
