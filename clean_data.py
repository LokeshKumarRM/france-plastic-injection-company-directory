import re
from urllib.parse import urlsplit, urlunsplit, unquote

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/france_plastic_injection_companies.csv"

OUTPUT_FILE = "data/france_plastic_injection_companies_cleaned.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("LOADING RAW DATA")
print("=" * 60)

# IMPORTANT:
# postal_code and source_number are identifiers.
# They must be loaded as strings so leading zeros are preserved.

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "source_number": str,
        "postal_code": str
    }
)

print("Raw records:", len(df))


# ============================================================
# COMPANY NAME CLEANING
# ============================================================

def clean_company_name(name):

    if pd.isna(name):
        return ""

    name = str(name)

    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    # Fix legal suffixes accidentally joined to names
    #
    # Chris-france PlastiquesSa
    # → Chris-france Plastiques Sa

    name = re.sub(
        r"([A-Za-zÀ-ÿ])SAS$",
        r"\1 SAS",
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(
        r"([A-Za-zÀ-ÿ])SARL$",
        r"\1 SARL",
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(
        r"([A-Za-zÀ-ÿ])SA$",
        r"\1 SA",
        name,
        flags=re.IGNORECASE
    )

    # Fix accidental number attached to company name
    #
    # ACTP Micro Injection89
    # → ACTP Micro Injection

    name = re.sub(
        r"([A-Za-zÀ-ÿ])(\d+)$",
        r"\1",
        name
    )

    return name.strip()


df["company_name"] = df["company_name"].apply(
    clean_company_name
)


# ============================================================
# PHONE CLEANING
# ============================================================

def clean_phone(phone):

    if pd.isna(phone):
        return ""

    phone = str(phone).strip()

    if phone == "":
        return ""

    if phone.startswith("+33"):

        digits = re.sub(
            r"\D",
            "",
            phone
        )

        # French international number:
        # +33 + 9 digits

        if len(digits) == 11:

            national_number = digits[2:]

            return (
                "+33 "
                + national_number[0]
                + " "
                + national_number[1:3]
                + " "
                + national_number[3:5]
                + " "
                + national_number[5:7]
                + " "
                + national_number[7:9]
            )

    return phone


df["phone"] = df["phone"].apply(
    clean_phone
)


# ============================================================
# WEBSITE CLEANING
# ============================================================

def clean_website(url):

    if pd.isna(url):
        return ""

    url = str(url).strip()

    if url == "":
        return ""

    # --------------------------------------------------------
    # Remove LinkedIn ADMIN URLs
    # --------------------------------------------------------

    if "linkedin.com" in url.lower():

        if "/admin/" in url.lower():

            return ""

    # --------------------------------------------------------
    # Decode URL encoding
    # --------------------------------------------------------

    url = unquote(url)

    # --------------------------------------------------------
    # Add HTTPS to www URLs
    # --------------------------------------------------------

    if url.startswith("www."):

        url = "https://" + url

    # --------------------------------------------------------
    # Remove query parameters
    # --------------------------------------------------------

    try:

        parsed = urlsplit(url)

        url = urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                "",
                ""
            )
        )

    except Exception:

        pass

    return url.rstrip("/")


df["website"] = df["website"].apply(
    clean_website
)


# ============================================================
# GENERAL TEXT CLEANING
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    value = str(value)

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


df["address"] = df["address"].apply(clean_text)

df["city"] = df["city"].apply(clean_text)

df["country"] = df["country"].apply(clean_text)


# ============================================================
# POSTAL CODE CLEANING
# ============================================================

def clean_postal_code(postal_code):

    if pd.isna(postal_code):
        return ""

    postal_code = str(postal_code).strip()

    if postal_code == "":
        return ""

    # Extract digits only
    digits = re.sub(
        r"\D",
        "",
        postal_code
    )

    # If it was read as 1430 instead of 01430,
    # restore the leading zero.
    #
    # 1430 → 01430

    if len(digits) == 4:

        digits = digits.zfill(5)

    # Keep valid French 5-digit postal codes

    if len(digits) == 5:

        return digits

    return ""


df["postal_code"] = df["postal_code"].apply(
    clean_postal_code
)


# ============================================================
# COUNTRY STANDARDIZATION
# ============================================================

df["country"] = "France"


# ============================================================
# SOURCE NUMBER CLEANING
# ============================================================

df["source_number"] = (
    df["source_number"]
    .astype(str)
    .str.strip()
)

# Restore 01, 02, 03 etc.
# Premium-01 remains unchanged.

def clean_source_number(value):

    value = str(value).strip()

    if value.startswith("Premium"):

        return value

    if value.isdigit():

        return value.zfill(2)

    return value


df["source_number"] = df["source_number"].apply(
    clean_source_number
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=[
        "company_name",
        "address",
        "postal_code"
    ],
    keep="first"
)

duplicates_removed = (
    before_duplicates - len(df)
)


# ============================================================
# MISSING VALUE REPORT
# ============================================================

missing_report = {}

for column in [
    "company_name",
    "address",
    "city",
    "postal_code",
    "phone",
    "website"
]:

    missing_report[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )


# ============================================================
# REORDER COLUMNS
# ============================================================

columns = [
    "source_number",
    "company_name",
    "address",
    "city",
    "postal_code",
    "country",
    "phone",
    "website",
    "source_url"
]

df = df[columns]


# ============================================================
# SORT RECORDS
# ============================================================

def sort_source_number(value):

    if str(value).startswith("Premium"):

        return 0

    try:

        return int(value)

    except ValueError:

        return 999


df["_sort_order"] = df["source_number"].apply(
    sort_source_number
)

df = df.sort_values(
    "_sort_order"
)

df = df.drop(
    columns=["_sort_order"]
)

df = df.reset_index(drop=True)


# ============================================================
# SAVE CLEANED DATA
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# CLEANING REPORT
# ============================================================

print()
print("=" * 60)
print("DATA CLEANING COMPLETED")
print("=" * 60)

print(
    "Raw records:        ",
    before_duplicates
)

print(
    "Duplicates removed: ",
    duplicates_removed
)

print(
    "Final records:      ",
    len(df)
)


# ============================================================
# MISSING VALUES
# ============================================================

print()
print("Missing values:")
print("-" * 40)

for column, count in missing_report.items():

    print(
        f"{column:<15}: {count}"
    )


# ============================================================
# DATA COVERAGE
# ============================================================

websites_available = (
    df["website"]
    .fillna("")
    .str.strip()
    .ne("")
    .sum()
)

phones_available = (
    df["phone"]
    .fillna("")
    .str.strip()
    .ne("")
    .sum()
)

postal_codes_available = (
    df["postal_code"]
    .fillna("")
    .str.strip()
    .ne("")
    .sum()
)


print()
print("=" * 60)
print("DATA COVERAGE")
print("=" * 60)

print(
    "Companies with website:",
    websites_available
)

print(
    "Companies with phone:",
    phones_available
)

print(
    "Companies with postal code:",
    postal_codes_available
)


# ============================================================
# SAMPLE
# ============================================================

print()
print("=" * 60)
print("CLEANED DATA SAMPLE")
print("=" * 60)

print(
    df.head(10).to_string(index=False)
)


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 60)
print("CLEANED CSV SAVED")
print("=" * 60)

print(OUTPUT_FILE)
