import requests
import pandas as pd
import time
import json
import os
import unicodedata


INPUT_FILE = "data/france_plastic_injection_companies_cleaned.csv"
OUTPUT_FILE = "data/france_plastic_injection_companies_final.csv"
CACHE_FILE = "data/geographic_lookup_cache.json"

API_URL = "https://geo.api.gouv.fr/communes"


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(value):
    """
    Normalize text so city names can be compared
    even when accents/capitalization are different.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    value = unicodedata.normalize("NFD", value)

    value = "".join(
        char
        for char in value
        if unicodedata.category(char) != "Mn"
    )

    return value


# --------------------------------------------------
# LOAD CACHE
# --------------------------------------------------

def load_cache():

    if os.path.exists(CACHE_FILE):

        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


# --------------------------------------------------
# SAVE CACHE
# --------------------------------------------------

def save_cache(cache):

    with open(CACHE_FILE, "w", encoding="utf-8") as file:

        json.dump(
            cache,
            file,
            ensure_ascii=False,
            indent=4
        )


# --------------------------------------------------
# GET GEOGRAPHIC INFORMATION
# --------------------------------------------------

def get_geographic_data(postal_code, city, cache):

    postal_code = str(postal_code).strip()

    city = "" if pd.isna(city) else str(city).strip()

    cache_key = f"{postal_code}|{normalize_text(city)}"

    # Check cache first
    if cache_key in cache:

        return cache[cache_key]


    params = {
        "codePostal": postal_code,
        "fields": "nom,code,codeDepartement,codeRegion",
        "format": "json"
    }


    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        results = response.json()


    except requests.RequestException as error:

        print(
            f"API error for {postal_code} - {city}: {error}"
        )

        result = {
            "department_code": "",
            "department": "",
            "region_code": "",
            "region": "",
            "geo_match_status": "api_error"
        }

        cache[cache_key] = result

        return result


    # --------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------

    if not results:

        result = {
            "department_code": "",
            "department": "",
            "region_code": "",
            "region": "",
            "geo_match_status": "not_found"
        }

        cache[cache_key] = result

        return result


    # --------------------------------------------------
    # TRY TO MATCH CITY
    # --------------------------------------------------

    normalized_city = normalize_text(city)

    city_matches = []

    if normalized_city:

        for item in results:

            api_city = normalize_text(
                item.get("nom", "")
            )

            if api_city == normalized_city:

                city_matches.append(item)


    # If city matched, use those results
    if city_matches:

        candidates = city_matches

    else:

        # Otherwise use all postal-code results
        candidates = results


    # --------------------------------------------------
    # UNIQUE DEPARTMENT / REGION COMBINATIONS
    # --------------------------------------------------

    combinations = set()

    for item in candidates:

        department_code = item.get(
            "codeDepartement",
            ""
        )

        region_code = item.get(
            "codeRegion",
            ""
        )

        combinations.add(
            (
                department_code,
                region_code
            )
        )


    # --------------------------------------------------
    # AMBIGUOUS RESULT
    # --------------------------------------------------

    if len(combinations) > 1:

        result = {
            "department_code": "",
            "department": "",
            "region_code": "",
            "region": "",
            "geo_match_status": "ambiguous"
        }

        cache[cache_key] = result

        return result


    # --------------------------------------------------
    # SINGLE RESULT
    # --------------------------------------------------

    department_code, region_code = next(
        iter(combinations)
    )


    # Department names
    department_url = (
        f"https://geo.api.gouv.fr/departements/"
        f"{department_code}"
    )

    region_url = (
        f"https://geo.api.gouv.fr/regions/"
        f"{region_code}"
    )


    try:

        department_response = requests.get(
            department_url,
            timeout=10
        )

        region_response = requests.get(
            region_url,
            timeout=10
        )

        department_response.raise_for_status()
        region_response.raise_for_status()

        department_data = department_response.json()
        region_data = region_response.json()

        department_name = department_data.get(
            "nom",
            ""
        )

        region_name = region_data.get(
            "nom",
            ""
        )

    except requests.RequestException:

        department_name = ""
        region_name = ""


    # --------------------------------------------------
    # MATCH STATUS
    # --------------------------------------------------

    if city_matches:

        status = "matched_city"

    else:

        status = "matched_postal_code"


    result = {

        "department_code": department_code,

        "department": department_name,

        "region_code": region_code,

        "region": region_name,

        "geo_match_status": status
    }


    cache[cache_key] = result

    return result


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print("=" * 60)
    print("FRANCE PLASTIC INJECTION")
    print("GEOGRAPHIC ENRICHMENT")
    print("=" * 60)


    # --------------------------------------------------
    # LOAD CLEANED DATA
    # --------------------------------------------------

    print("\nLoading cleaned dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        dtype=str
    )


    print(f"Records loaded: {len(df)}")


    # --------------------------------------------------
    # LOAD CACHE
    # --------------------------------------------------

    cache = load_cache()

    print(
        f"Cached geographic lookups: {len(cache)}"
    )


    # --------------------------------------------------
    # CREATE NEW COLUMNS
    # --------------------------------------------------

    df["department_code"] = ""

    df["department"] = ""

    df["region_code"] = ""

    df["region"] = ""

    df["geo_match_status"] = ""


    # --------------------------------------------------
    # PROCESS RECORDS
    # --------------------------------------------------

    total = len(df)

    for index, row in df.iterrows():

        postal_code = row.get(
            "postal_code",
            ""
        )

        city = row.get(
            "city",
            ""
        )


        if (
            pd.isna(postal_code)
            or str(postal_code).strip() == ""
        ):

            df.at[
                index,
                "geo_match_status"
            ] = "missing_postal_code"

            continue


        print(
            f"[{index + 1}/{total}] "
            f"{row['company_name']} "
            f"→ {postal_code} "
            f"{city}"
        )


        geographic_data = get_geographic_data(
            postal_code,
            city,
            cache
        )


        df.at[
            index,
            "department_code"
        ] = geographic_data[
            "department_code"
        ]


        df.at[
            index,
            "department"
        ] = geographic_data[
            "department"
        ]


        df.at[
            index,
            "region_code"
        ] = geographic_data[
            "region_code"
        ]


        df.at[
            index,
            "region"
        ] = geographic_data[
            "region"
        ]


        df.at[
            index,
            "geo_match_status"
        ] = geographic_data[
            "geo_match_status"
        ]


        # Small delay so we don't unnecessarily
        # hammer the public API.
        time.sleep(0.1)


    # --------------------------------------------------
    # SAVE CACHE
    # --------------------------------------------------

    save_cache(cache)


    # --------------------------------------------------
    # SAVE FINAL DATASET
    # --------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("GEOGRAPHIC ENRICHMENT COMPLETED")
    print("=" * 60)


    print(
        f"\nTotal records: {len(df)}"
    )


    print(
        "\nGeographic match status:"
    )

    print(
        df["geo_match_status"]
        .value_counts(dropna=False)
    )


    print(
        "\nDepartments found:",
        df["department"]
        .replace("", pd.NA)
        .notna()
        .sum()
    )


    print(
        "Regions found:",
        df["region"]
        .replace("", pd.NA)
        .notna()
        .sum()
    )


    print(
        "\nFinal dataset columns:"
    )

    print(
        df.columns.tolist()
    )


    print(
        "\nFINAL CSV SAVED:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()