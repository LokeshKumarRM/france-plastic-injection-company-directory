import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

INPUT_FILE = "data/france_plastic_injection_companies_final.csv"

OUTPUT_FILE = "data/France_Plastic_Injection_Company_Directory.xlsx"


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("=" * 60)
print("FRANCE PLASTIC INJECTION")
print("EXCEL COMPANY DIRECTORY")
print("=" * 60)

print("\nLoading final CSV...")

df = pd.read_csv(
    INPUT_FILE,
    dtype=str
)

print(f"Records loaded: {len(df)}")


# --------------------------------------------------
# CLEAN EMPTY VALUES
# --------------------------------------------------

df = df.fillna("")


# --------------------------------------------------
# SELECT COLUMNS
# --------------------------------------------------

desired_columns = [
    "source_number",
    "company_name",
    "address",
    "city",
    "postal_code",
    "department_code",
    "department",
    "region_code",
    "region",
    "country",
    "phone",
    "website",
    "source_url",
    "geo_match_status"
]

columns = [
    column
    for column in desired_columns
    if column in df.columns
]

df = df[columns]


# --------------------------------------------------
# RENAME COLUMNS
# --------------------------------------------------

column_names = {
    "source_number": "Source No.",
    "company_name": "Company Name",
    "address": "Address",
    "city": "City",
    "postal_code": "Postal Code",
    "department_code": "Department Code",
    "department": "Department",
    "region_code": "Region Code",
    "region": "Region",
    "country": "Country",
    "phone": "Phone",
    "website": "Website",
    "source_url": "Source URL",
    "geo_match_status": "Geo Match Status"
}

df.rename(
    columns=column_names,
    inplace=True
)


# --------------------------------------------------
# CREATE EXCEL FILE
# --------------------------------------------------

print("\nCreating Excel workbook...")

with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Company Directory",
        index=False
    )


# --------------------------------------------------
# OPEN WORKBOOK
# --------------------------------------------------

workbook = load_workbook(
    OUTPUT_FILE
)

directory = workbook["Company Directory"]


# --------------------------------------------------
# FREEZE HEADER
# --------------------------------------------------

directory.freeze_panes = "A2"


# --------------------------------------------------
# CREATE EXCEL TABLE
# --------------------------------------------------

last_row = directory.max_row
last_column = directory.max_column

last_column_letter = get_column_letter(
    last_column
)

table_reference = (
    f"A1:{last_column_letter}{last_row}"
)

table = Table(
    displayName="CompanyDirectory",
    ref=table_reference
)

table_style = TableStyleInfo(
    name="TableStyleMedium2",
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False
)

table.tableStyleInfo = table_style

directory.add_table(table)


# --------------------------------------------------
# HEADER FORMATTING
# --------------------------------------------------

for cell in directory[1]:

    cell.font = Font(
        bold=True,
        color="FFFFFF"
    )

    cell.alignment = Alignment(
        horizontal="center",
        vertical="center"
    )


# --------------------------------------------------
# BODY FORMATTING
# --------------------------------------------------

for row in directory.iter_rows(
    min_row=2
):

    for cell in row:

        cell.alignment = Alignment(
            vertical="top",
            wrap_text=True
        )


# --------------------------------------------------
# WEBSITE LINKS
# --------------------------------------------------

website_column = None

for cell in directory[1]:

    if cell.value == "Website":
        website_column = cell.column
        break


if website_column:

    for row in range(
        2,
        directory.max_row + 1
    ):

        cell = directory.cell(
            row=row,
            column=website_column
        )

        url = str(cell.value).strip()

        if url:

            if not url.startswith(
                ("http://", "https://")
            ):

                url = "https://" + url

            cell.value = url
            cell.hyperlink = url

            cell.font = Font(
                color="0563C1",
                underline="single"
            )


# --------------------------------------------------
# SOURCE URL LINKS
# --------------------------------------------------

source_column = None

for cell in directory[1]:

    if cell.value == "Source URL":
        source_column = cell.column
        break


if source_column:

    for row in range(
        2,
        directory.max_row + 1
    ):

        cell = directory.cell(
            row=row,
            column=source_column
        )

        url = str(cell.value).strip()

        if url:

            if not url.startswith(
                ("http://", "https://")
            ):

                url = "https://" + url

            cell.value = url
            cell.hyperlink = url

            cell.font = Font(
                color="0563C1",
                underline="single"
            )


# --------------------------------------------------
# COLUMN WIDTHS
# --------------------------------------------------

column_widths = {
    "A": 12,
    "B": 45,
    "C": 50,
    "D": 30,
    "E": 14,
    "F": 18,
    "G": 25,
    "H": 14,
    "I": 30,
    "J": 15,
    "K": 22,
    "L": 38,
    "M": 45,
    "N": 18,
    "O": 22
}

for column, width in column_widths.items():

    directory.column_dimensions[
        column
    ].width = width


directory.row_dimensions[1].height = 30


# --------------------------------------------------
# SUMMARY SHEET
# --------------------------------------------------

summary = workbook.create_sheet(
    "Summary"
)


summary["A1"] = (
    "France Plastic Injection "
    "Company Directory"
)

summary["A1"].font = Font(
    bold=True,
    size=18
)

summary["A1"].alignment = Alignment(
    horizontal="center"
)

summary.merge_cells("A1:D1")


# --------------------------------------------------
# SUMMARY STATISTICS
# --------------------------------------------------

total_companies = len(df)

companies_with_website = (
    df["Website"]
    .replace("", pd.NA)
    .notna()
    .sum()
)

companies_with_phone = (
    df["Phone"]
    .replace("", pd.NA)
    .notna()
    .sum()
)

companies_with_department = (
    df["Department"]
    .replace("", pd.NA)
    .notna()
    .sum()
)

companies_with_region = (
    df["Region"]
    .replace("", pd.NA)
    .notna()
    .sum()
)


summary_data = [
    ["Metric", "Value"],
    ["Total Companies", total_companies],
    ["Companies with Website", companies_with_website],
    ["Companies with Phone", companies_with_phone],
    ["Companies with Department", companies_with_department],
    ["Companies with Region", companies_with_region]
]


for row in summary_data:
    summary.append(row)


# --------------------------------------------------
# SUMMARY HEADER
# --------------------------------------------------

for cell in summary[3]:

    cell.font = Font(
        bold=True,
        color="FFFFFF"
    )

    cell.alignment = Alignment(
        horizontal="center"
    )


# --------------------------------------------------
# REGION SUMMARY
# --------------------------------------------------

start_row = 11

summary.cell(
    start_row,
    1,
    "Companies by Region"
)

summary.cell(
    start_row,
    1
).font = Font(
    bold=True,
    size=14
)


region_counts = (
    df[
        df["Region"] != ""
    ]["Region"]
    .value_counts()
)


summary.cell(
    start_row + 1,
    1,
    "Region"
)

summary.cell(
    start_row + 1,
    2,
    "Companies"
)


current_row = start_row + 2

for region, count in region_counts.items():

    summary.cell(
        current_row,
        1,
        region
    )

    summary.cell(
        current_row,
        2,
        int(count)
    )

    current_row += 1


# --------------------------------------------------
# DEPARTMENT SUMMARY
# --------------------------------------------------

department_start = current_row + 2

summary.cell(
    department_start,
    1,
    "Companies by Department"
)

summary.cell(
    department_start,
    1
).font = Font(
    bold=True,
    size=14
)


department_counts = (
    df[
        df["Department"] != ""
    ]["Department"]
    .value_counts()
)


summary.cell(
    department_start + 1,
    1,
    "Department"
)

summary.cell(
    department_start + 1,
    2,
    "Companies"
)


current_row = department_start + 2

for department, count in department_counts.items():

    summary.cell(
        current_row,
        1,
        department
    )

    summary.cell(
        current_row,
        2,
        int(count)
    )

    current_row += 1


# --------------------------------------------------
# SUMMARY COLUMN WIDTHS
# --------------------------------------------------

summary.column_dimensions["A"].width = 35
summary.column_dimensions["B"].width = 20
summary.column_dimensions["C"].width = 20
summary.column_dimensions["D"].width = 20


# --------------------------------------------------
# SAVE
# --------------------------------------------------

workbook.save(
    OUTPUT_FILE
)


# --------------------------------------------------
# FINAL OUTPUT
# --------------------------------------------------

print("\n" + "=" * 60)
print("EXCEL DIRECTORY CREATED SUCCESSFULLY")
print("=" * 60)

print(
    f"\nCompanies exported: {total_companies}"
)

print(
    f"Companies with website: "
    f"{companies_with_website}"
)

print(
    f"Companies with phone: "
    f"{companies_with_phone}"
)

print(
    f"Companies with department: "
    f"{companies_with_department}"
)

print(
    f"Companies with region: "
    f"{companies_with_region}"
)

print("\nExcel file:")

print(OUTPUT_FILE)