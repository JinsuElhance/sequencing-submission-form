import os
import re
import math
import logging
import json
import pandas as pd

logger = logging.getLogger("my_app_logger")


def get_columns_data():
    current_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    columns_file_path = os.path.join(
        base_dir, "metadataconfig", "columns.json"
    )

    with open(columns_file_path, "r") as columns_file:
        data = json.load(columns_file)

    for key, value in data.items():
        lookup_file = value.get("lookup_file")
        if (
            lookup_file and lookup_file.strip()
        ):  # Check if lookup_file is not empty
            lookup_file_path = os.path.join(
                base_dir, "metadataconfig", lookup_file
            )
            if os.path.exists(lookup_file_path):
                with open(lookup_file_path, "r") as lookup:
                    value["options"] = lookup.read().strip().split("\n")
            else:
                value["options"] = []  # or handle missing file as needed

    return data


def check_expected_columns(df, expected_columns_data):
    """
    Check for missing and extra columns in the DataFrame.
    """

    expected_columns = list(expected_columns_data.keys())
    uploaded_columns = df.columns.tolist()
    missing_columns = list(set(expected_columns) - set(uploaded_columns))
    extra_columns = list(set(uploaded_columns) - set(expected_columns))
    issues = []

    if missing_columns:
        issues.append(
            {
                "invalid": missing_columns,
                "message": "Missing columns",
                "status": 0,
            }
        )

    if extra_columns:
        issues.append(
            {"invalid": extra_columns, "message": "Extra columns", "status": 0}
        )
    return issues


def check_sample_id(sample_id):
    """
    Check if a given SampleID follows the format:
    location name (letters), followed by year (two digits),
    an underscore, and a sample number (one or more digits).
    """
    sample_id_pattern = re.compile(r"^[A-Za-z]+[0-9]{2}_[0-9]+$")
    if not sample_id_pattern.match(str(sample_id)):
        return {"status": 0, "message": "Invalid value"}
    else:
        return {"status": 1, "message": "Valid value"}


def check_sequencing_facility(value):
    return check_field_length_value(value, 150)


def check_vegetation(value):
    return check_field_length_value(value, 200)


def check_expedition_lead(value):
    return check_field_length_value(value, 150)


def check_notes(value):
    return check_field_length_value(value, 200)


def check_collaborators_value(value):
    return check_field_length_value(value, 150)


def check_field_length_value(value, max_length):
    """
    Check if a single value's length does not exceed the specified maximum length.
    """
    if len(str(value)) > max_length:
        return {
            "status": 0,
            "message": f"Value exceeds maximum length of {max_length}",
        }
    else:
        return {"status": 1, "message": "Valid value"}


def check_agricultural_land_value(value):
    """
    Check if a single Agricultural_land value is valid ('yes' or 'no').
    """
    if value not in ["yes", "no"]:
        return {"status": 0, "message": "Invalid value"}
    else:
        return {"status": 1, "message": "Valid value"}


def check_field_values_lookup(df, valid_values, field_name, allow_empty=True):
    """
    Check if field_name values are valid based on the valid_values list.
    Ignore case when comparing values.
    """
    invalid_values = [
        {"row": idx, "value": value}
        for idx, value in df[field_name].dropna().items()
        if (
            (value.strip() == "" and not allow_empty)
            or (value.strip().lower() not in [v.lower() for v in valid_values])
        )
    ]

    # Identify empty values
    empty_values = []
    if not allow_empty:
        empty_values = df[
            df[field_name].isna()
            | df[field_name].astype(str).str.strip().eq("")
        ].index.tolist()

    if invalid_values or empty_values:
        return {
            "invalid": invalid_values,
            "empty_values": empty_values,
            "message": (
                "Invalid " + field_name + " values"
                if invalid_values
                else "Empty values found for " + field_name
            ),
            "status": 0,
        }
    else:
        return {"status": 1}


def check_date_collected(date):
    """
    Check if a single Date_collected value is in DD/MM/YYYY format.
    """
    date_format = r"\b(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/\d{4}\b"

    if not re.match(date_format, str(date)):
        return {"status": 0, "message": "Invalid value"}
    else:
        return {"status": 1, "message": "Valid value"}


def check_dna_concentration(value):
    """
    Check if a single DNA_concentration_ng_ul value is a valid numeric value.
    """
    if not is_numeric(value):
        return {"status": 0, "message": "Invalid value"}
    else:
        return {"status": 1, "message": "Valid value"}


def check_elevation_value(value):
    """
    Check if a single elevation value is a valid positive integer.
    """
    if not is_positive_integer(value):
        return {"status": 0, "message": "Invalid value"}
    else:
        return {"status": 1, "message": "Valid value"}


def is_numeric(value):
    """
    Check if a value is a numeric decimal.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_positive_integer(value):
    """
    Check if a value is a positive integer.
    """
    try:
        # Check if the value can be converted to an integer
        int_value = int(value)
        # Check if the integer value is positive
        if int_value > 0:
            return True
        else:
            return False
    except ValueError:
        return False


def check_latitude_longitude(value):
    """
    Check if a single latitude or longitude value is in decimal format (WGS1984) and valid.
    """

    try:
        float_value = float(value)
        if -90 <= float_value <= 90:  # Valid latitude range
            if re.match(
                r"^-?\d+(\.\d{1,6})?$", str(float_value)
            ):  # Check precision up to 6 decimal places
                return {"status": 1, "message": "Valid latitude"}
            else:
                return {
                    "status": 0,
                    "message": "Invalid value: incorrect precision",
                }
        elif -180 <= float_value <= 180:  # Valid longitude range
            if re.match(
                r"^-?\d+(\.\d{1,6})?$", str(float_value)
            ):  # Check precision up to 6 decimal places
                return {"status": 1, "message": "Valid longitude"}
            else:
                return {
                    "status": 0,
                    "message": "Invalid value: incorrect precision",
                }
        else:
            return {"status": 0, "message": "Invalid value: out of range"}
    except ValueError:
        return {"status": 0, "message": "Invalid value: not a valid number"}


def check_metadata(df, using_scripps):
    """
    Check metadata including columns, and validity of fields.
    """
    expected_columns_data = (
        get_columns_data()
    )  # Replace with your function to fetch column metadata
    overall_status = 1
    issues = {}

    for key, value in expected_columns_data.items():
        if (
            "required" in value
            and value["required"] == "IfNotScripps"
        ):
            if using_scripps == "no":
                value["required"] = True
            else:
                value["required"] = False                
            

    for column_key, column_values in expected_columns_data.items():
        if column_key not in df.columns:
            if column_values.get("required", False):
                issues[column_key] = {
                    "status": 0,
                    "message": f"Required column {column_key} is missing",
                    "empty_values": True,  # Indicate that the column is required but missing
                }
                overall_status = 0
            continue  # Skip further checks for missing columns

        # Check if the field is required but has empty values
        column_data = df[column_key]
        if column_values.get("required", False):
            empty_values = column_data.isna() | column_data.astype(
                str
            ).str.strip().eq("")
            if empty_values.any():
                issues[column_key] = {
                    "status": 0,
                    "message": f"Required column {column_key} has empty values",
                    "empty_values": empty_values[empty_values].index.tolist(),
                }
                overall_status = 0
                continue  # Skip further checks for this column if empty values found

        # Perform specific checks based on the type of validation
        if "check_function" in column_values:
            check_function_name = column_values["check_function"]
            if check_function_name in globals():
                check_function = globals()[check_function_name]
                invalid_entries = []
                for idx, value in column_data.items():
                    # Skip validation for empty, None, or NaN values
                    if (
                        value is None
                        or value == ""
                        or (isinstance(value, float) and math.isnan(value))
                    ):
                        continue

                    check_result = check_function(value)
                    if check_result["status"] == 0:
                        invalid_entries.append(
                            {
                                "row": idx,
                                "value": value,
                                "message": check_result["message"],
                            }
                        )

                if invalid_entries:
                    overall_status = 0
                    issues[column_key] = {
                        "status": 0,
                        "invalid": invalid_entries,
                        "message": f"Column {column_key} has invalid values",
                    }
            else:
                overall_status = 0
                issues[column_key] = {
                    "status": 0,
                    "message": f"Check function {check_function_name} not found",
                }

    final_result = {"status": overall_status}
    final_result.update(issues)

    return final_result
