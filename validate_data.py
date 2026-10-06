import re
from urllib.parse import urlparse

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/france_plastic_injection_companies_cleaned.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("LOADING CLEANED DATA")
print("=" * 60)

df = pd.read_csv(
    INPUT_FILE,
    dtype={
        "source_number": str,
        "postal_code": str
    }
)

print("Records loaded:", len(df))


# ============================================================
# 1. CHECK DUPLICATE RECORDS
# ============================================================

print()
print("=" * 60)
print("1. DUPLICATE RECORD CHECK")
print("=" * 60)

duplicate_records = df.duplicated(
    subset=[
        "company_name",
        "address",
        "postal_code"
    ],
    keep=False
)

duplicate_count = duplicate_records.sum()

print(
    "Duplicate records:",
    duplicate_count
)

if duplicate_count > 0:

    print()
    print("Duplicate records found:")

    print(
        df[duplicate_records][
            [
                "company_name",
                "address",
                "postal_code"
            ]
        ].to_string(index=False)
    )

else:

    print("No duplicate records found.")


# ============================================================
# 2. CHECK DUPLICATE COMPANY NAMES
# ============================================================

print()
print("=" * 60)
print("2. DUPLICATE COMPANY NAME CHECK")
print("=" * 60)

duplicate_names = (
    df[
        df["company_name"].duplicated(
            keep=False
        )
    ]
    .sort_values("company_name")
)

if len(duplicate_names) > 0:

    print(
        "Companies with duplicate names:",
        len(duplicate_names)
    )

    print()

    print(
        duplicate_names[
            [
                "company_name",
                "city",
                "postal_code"
            ]
        ].to_string(index=False)
    )

else:

    print("No duplicate company names found.")


# ============================================================
# 3. POSTAL CODE VALIDATION
# ============================================================

print()
print("=" * 60)
print("3. POSTAL CODE VALIDATION")
print("=" * 60)


def is_valid_postal_code(value):

    if pd.isna(value):

        return False

    value = str(value).strip()

    return bool(
        re.fullmatch(
            r"\d{5}",
            value
        )
    )


invalid_postal_codes = df[
    ~df["postal_code"].apply(
        is_valid_postal_code
    )
    & df["postal_code"].notna()
    & (
        df["postal_code"]
        .astype(str)
        .str.strip()
        != ""
    )
]

print(
    "Invalid postal codes:",
    len(invalid_postal_codes)
)

if len(invalid_postal_codes) > 0:

    print()

    print(
        invalid_postal_codes[
            [
                "company_name",
                "postal_code",
                "city"
            ]
        ].to_string(index=False)
    )

else:

    print("All available postal codes have 5 digits.")


# ============================================================
# 4. PHONE VALIDATION
# ============================================================

print()
print("=" * 60)
print("4. PHONE VALIDATION")
print("=" * 60)


def is_valid_phone(phone):

    if pd.isna(phone):

        return False

    phone = str(phone).strip()

    if phone == "":

        return False

    # Expected cleaned French format:
    #
    # +33 X XX XX XX XX

    return bool(
        re.fullmatch(
            r"\+33\s\d\s\d{2}\s\d{2}\s\d{2}\s\d{2}",
            phone
        )
    )


available_phones = df[
    df["phone"]
    .fillna("")
    .astype(str)
    .str.strip()
    != ""
]

invalid_phones = available_phones[
    ~available_phones["phone"].apply(
        is_valid_phone
    )
]

print(
    "Phones available:",
    len(available_phones)
)

print(
    "Invalid phone formats:",
    len(invalid_phones)
)

if len(invalid_phones) > 0:

    print()

    print(
        invalid_phones[
            [
                "company_name",
                "phone"
            ]
        ].to_string(index=False)
    )

else:

    print("All available phone numbers have the expected format.")


# ============================================================
# 5. WEBSITE VALIDATION
# ============================================================

print()
print("=" * 60)
print("5. WEBSITE VALIDATION")
print("=" * 60)


def is_valid_url(url):

    if pd.isna(url):

        return False

    url = str(url).strip()

    if url == "":

        return False

    try:

        parsed = urlparse(url)

        return (
            parsed.scheme in ["http", "https"]
            and bool(parsed.netloc)
        )

    except Exception:

        return False


available_websites = df[
    df["website"]
    .fillna("")
    .astype(str)
    .str.strip()
    != ""
]

invalid_websites = available_websites[
    ~available_websites["website"].apply(
        is_valid_url
    )
]

print(
    "Websites available:",
    len(available_websites)
)

print(
    "Invalid website URLs:",
    len(invalid_websites)
)

if len(invalid_websites) > 0:

    print()

    print(
        invalid_websites[
            [
                "company_name",
                "website"
            ]
        ].to_string(index=False)
    )

else:

    print("All available website URLs have valid URL structure.")


# ============================================================
# 6. LINKEDIN ADMIN URL CHECK
# ============================================================

print()
print("=" * 60)
print("6. LINKEDIN ADMIN URL CHECK")
print("=" * 60)

linkedin_admin = df[
    df["website"]
    .fillna("")
    .astype(str)
    .str.contains(
        "linkedin.com/.*/admin|linkedin.com/company/.*/admin",
        case=False,
        regex=True
    )
]

print(
    "LinkedIn admin URLs remaining:",
    len(linkedin_admin)
)

if len(linkedin_admin) > 0:

    print(
        linkedin_admin[
            [
                "company_name",
                "website"
            ]
        ].to_string(index=False)
    )

else:

    print("No LinkedIn admin URLs found.")


# ============================================================
# 7. MISSING VALUE CHECK
# ============================================================

print()
print("=" * 60)
print("7. MISSING VALUE CHECK")
print("=" * 60)

for column in [
    "company_name",
    "address",
    "city",
    "postal_code",
    "phone",
    "website"
]:

    missing = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    print(
        f"{column:<15}: {missing}"
    )


# ============================================================
# 8. SOURCE NUMBER CHECK
# ============================================================

print()
print("=" * 60)
print("8. SOURCE NUMBER CHECK")
print("=" * 60)

source_numbers = []

for value in df["source_number"]:

    value = str(value).strip()

    if value.startswith("Premium"):

        continue

    try:

        source_numbers.append(
            int(value)
        )

    except ValueError:

        pass


source_numbers = sorted(
    source_numbers
)

expected_numbers = list(
    range(
        1,
        120
    )
)

missing_numbers = sorted(
    set(expected_numbers)
    - set(source_numbers)
)

extra_numbers = sorted(
    set(source_numbers)
    - set(expected_numbers)
)

print(
    "Numbered records found:",
    len(source_numbers)
)

print(
    "Missing source numbers:",
    missing_numbers
)

print(
    "Unexpected source numbers:",
    extra_numbers
)


# ============================================================
# 9. COMPANY NAME SUSPICION CHECK
# ============================================================

print()
print("=" * 60)
print("9. SUSPICIOUS COMPANY NAME CHECK")
print("=" * 60)

suspicious_names = df[
    df["company_name"].str.contains(
        r"\d+$|SAS$|SARL$|SA$",
        case=False,
        regex=True,
        na=False
    )
]

print(
    "Names ending with legal suffix/number:",
    len(suspicious_names)
)

if len(suspicious_names) > 0:

    print()

    print(
        suspicious_names[
            [
                "source_number",
                "company_name"
            ]
        ].to_string(index=False)
    )


# ============================================================
# FINAL VALIDATION SUMMARY
# ============================================================

print()
print("=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

print(
    "Total records:",
    len(df)
)

print(
    "Duplicate records:",
    duplicate_count
)

print(
    "Invalid postal codes:",
    len(invalid_postal_codes)
)

print(
    "Invalid phone formats:",
    len(invalid_phones)
)

print(
    "Invalid website URLs:",
    len(invalid_websites)
)

print(
    "LinkedIn admin URLs:",
    len(linkedin_admin)
)

print(
    "Missing source numbers:",
    len(missing_numbers)
)

print()
print("=" * 60)
print("VALIDATION COMPLETED")
print("=" * 60)