import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

URL = "https://equipement-professionnel-france.fr/metier/entreprise-d-injection-plastique/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

OUTPUT_FILE = "data/france_plastic_injection_companies.csv"


# ============================================================
# DOWNLOAD PAGE
# ============================================================

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

print("Status code:", response.status_code)

response.raise_for_status()


# ============================================================
# PARSE HTML
# ============================================================

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text("\n", strip=True)

lines = [
    line.strip()
    for line in text.splitlines()
    if line.strip()
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_record_number(line):
    """
    Detect company numbers such as:

    01
    09
    68
    99
    100
    119
    """

    return bool(re.fullmatch(r"\d{1,3}", line))


def clean_company_name(name):
    """
    Clean unnecessary whitespace from company names.
    """

    name = re.sub(r"\s+", " ", name)

    return name.strip()


def extract_address(address):

    # Example:
    # 16 Av. des Catelines, 69720 Saint-Laurent-de-Mure, France

    match = re.search(
        r"^(.*?),\s*(\d{5})(?:\s+(.+?))?,\s*France$",
        address
    )

    if match:

        street = match.group(1).strip()
        postal_code = match.group(2).strip()
        city = match.group(3).strip() if match.group(3) else ""

        return street, postal_code, city

    return address.strip(), "", ""


def looks_like_phone(line):

    return bool(
        re.match(
            r"^\+33\s",
            line
        )
    )


def looks_like_website(line):

    return (
        line.startswith("http://")
        or line.startswith("https://")
        or line.startswith("www.")
    )


def looks_like_address(line):

    return bool(
        re.search(
            r"\d{5}.*France$",
            line
        )
    )


# ============================================================
# SCRAPE RECORDS
# ============================================================

companies = []

i = 0

while i < len(lines):

    current_line = lines[i]

    # --------------------------------------------------------
    # Detect company number
    # --------------------------------------------------------

    if not is_record_number(current_line):

        i += 1
        continue

    company_number = current_line

    # --------------------------------------------------------
    # Collect the following lines until we find
    # "En activité" / "Premium"
    # --------------------------------------------------------

    temp = []

    j = i + 1

    while j < len(lines):

        line = lines[j]

        # Stop when next company number appears
        if (
            is_record_number(line)
            and len(temp) > 0
        ):
            break

        # Stop after reaching another major section
        if line in [
            "À propos",
            "Tous les établissements",
            "Sélection premium"
        ]:
            break

        temp.append(line)

        # Once we have found the status and address,
        # we can continue collecting phone and website.
        #
        # Stop after rating information.
        if re.search(
            r"\d+(?:\.\d+)?\s*\(\d+\)$",
            line
        ):
            break

        j += 1

    # --------------------------------------------------------
    # Find status
    # --------------------------------------------------------

    status_index = None

    for index, line in enumerate(temp):

        if (
            line == "En activité"
            or line == "Premium"
            or "En activité" in line
        ):
            status_index = index
            break

    if status_index is None:

        i = j
        continue

    # --------------------------------------------------------
    # Company name
    #
    # Everything between company number and status.
    # Ignore obvious "Image:" text.
    # --------------------------------------------------------

    name_parts = []

    for line in temp[:status_index]:

        if line.startswith("Image:"):
            continue

        name_parts.append(line)

    company_name = " ".join(name_parts)

    company_name = clean_company_name(company_name)

    # --------------------------------------------------------
    # Find address
    # --------------------------------------------------------

    address = ""

    address_index = None

    for index in range(
        status_index + 1,
        len(temp)
    ):

        line = temp[index]

        if looks_like_address(line):

            address = line
            address_index = index
            break

    if not address:

        i = j
        continue

    # --------------------------------------------------------
    # Address components
    # --------------------------------------------------------

    street, postal_code, city = extract_address(address)

    # --------------------------------------------------------
    # Find phone
    # --------------------------------------------------------

    phone = ""

    for line in temp:

        if looks_like_phone(line):

            phone = line
            break

    # --------------------------------------------------------
    # Find website
    # --------------------------------------------------------

    website = ""

    for line in temp:

        if looks_like_website(line):

            website = line
            break

    # --------------------------------------------------------
    # Store record
    # --------------------------------------------------------

    companies.append({
        "source_number": company_number,
        "company_name": company_name,
        "address": street,
        "city": city,
        "postal_code": postal_code,
        "country": "France",
        "phone": phone,
        "website": website,
        "source_url": URL
    })

    i = j


# ============================================================
# ADD PREMIUM COMPANY
# ============================================================

premium_company = {
    "source_number": "Premium-01",
    "company_name": "Martin Plastiques Innovation",
    "address": "1 Chem. de l'Allier",
    "city": "Bourg-Argental",
    "postal_code": "42220",
    "country": "France",
    "phone": "+33 4 77 40 21 50",
    "website": "https://martin-plastiques-innovation.fr/",
    "source_url": URL
}

companies.append(premium_company)


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(companies)


# ============================================================
# CLEAN DATA
# ============================================================

df = df.drop_duplicates(
    subset=[
        "company_name",
        "address",
        "postal_code"
    ]
)


# Sort normal records first, premium last
def sort_number(value):

    if value == "Premium-01":
        return 999

    try:
        return int(value)
    except ValueError:
        return 999


df["_sort"] = df["source_number"].apply(sort_number)

df = df.sort_values("_sort")

df = df.drop(columns=["_sort"])


# Reset index
df = df.reset_index(drop=True)


# ============================================================
# SAVE CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 60)
print("SCRAPING COMPLETED")
print("=" * 60)

print("Companies found:", len(df))

print()
print(df.to_string(index=False))

print()
print("=" * 60)
print("CSV SAVED")
print("=" * 60)

print(OUTPUT_FILE)