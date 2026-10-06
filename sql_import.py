import pandas as pd
import pyodbc


# ============================================================
# CONFIGURATION
# ============================================================

SERVER = r"LOKEE\SQLEXPRESS01"

DATABASE = "FrancePlasticInjectionDB"

INPUT_FILE = "data/france_plastic_injection_companies_final.csv"


# ============================================================
# CONNECT TO SQL SERVER
# ============================================================

print("=" * 60)
print("FRANCE PLASTIC INJECTION")
print("SQL SERVER DATA IMPORT")
print("=" * 60)

print("\nConnecting to SQL Server...")

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)


try:

    connection = pyodbc.connect(
        connection_string
    )

    cursor = connection.cursor()

    print("SQL Server connection successful.")


except pyodbc.Error as error:

    print("\nSQL Server connection failed.")

    print(error)

    raise SystemExit


# ============================================================
# LOAD CSV
# ============================================================

print("\nLoading final CSV...")

df = pd.read_csv(
    INPUT_FILE,
    dtype=str
)

df = df.fillna("")

print(
    f"Records loaded from CSV: {len(df)}"
)


# ============================================================
# CHECK EXISTING RECORDS
# ============================================================

cursor.execute(
    "SELECT COUNT(*) FROM PlasticInjectionCompanies"
)

existing_count = cursor.fetchone()[0]

print(
    f"Records already in SQL table: {existing_count}"
)


# ============================================================
# PREVENT DUPLICATE IMPORT
# ============================================================

if existing_count > 0:

    print(
        "\nThe SQL table already contains data."
    )

    print(
        "Import cancelled to prevent duplicates."
    )

    connection.close()

    raise SystemExit


# ============================================================
# INSERT DATA
# ============================================================

print("\nStarting data import...")

insert_query = """
INSERT INTO PlasticInjectionCompanies
(
    SourceNo,
    CompanyName,
    Address,
    City,
    PostalCode,
    DepartmentCode,
    Department,
    RegionCode,
    Region,
    Country,
    Phone,
    Website,
    SourceURL,
    GeoMatchStatus
)
VALUES
(
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
)
"""


inserted_count = 0


for index, row in df.iterrows():

    values = (
        row.get("source_number", ""),
        row.get("company_name", ""),
        row.get("address", ""),
        row.get("city", ""),
        row.get("postal_code", ""),
        row.get("department_code", ""),
        row.get("department", ""),
        row.get("region_code", ""),
        row.get("region", ""),
        row.get("country", ""),
        row.get("phone", ""),
        row.get("website", ""),
        row.get("source_url", ""),
        row.get("geo_match_status", "")
    )

    cursor.execute(
        insert_query,
        values
    )

    inserted_count += 1

    print(
        f"[{inserted_count}/{len(df)}] "
        f"{row.get('company_name', '')}"
    )


# ============================================================
# COMMIT
# ============================================================

connection.commit()


# ============================================================
# VERIFY IMPORT
# ============================================================

cursor.execute(
    "SELECT COUNT(*) FROM PlasticInjectionCompanies"
)

final_count = cursor.fetchone()[0]


# ============================================================
# CLOSE CONNECTION
# ============================================================

connection.close()


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("SQL SERVER IMPORT COMPLETED")
print("=" * 60)

print(
    f"\nCSV records:       {len(df)}"
)

print(
    f"Records inserted:  {inserted_count}"
)

print(
    f"SQL table records:  {final_count}"
)


if final_count == len(df):

    print(
        "\nSUCCESS: All records were imported correctly."
    )

else:

    print(
        "\nWARNING: Record counts do not match."
    )