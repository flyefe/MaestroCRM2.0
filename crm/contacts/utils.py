from datetime import datetime

def parse_date(value):
    """Try parsing a date from multiple formats."""
    date_formats = [
        '%d/%m/%Y',  # Day/Month/Year
        '%Y-%m-%d',  # ISO standard
        '%m/%d/%Y',  # Month/Day/Year
        '%d-%m-%Y',  # Day-Month-Year
        '%m-%d-%Y',  # Month-Day-Year
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    # If all formats fail, raise an error
    raise ValueError(f"Unrecognized date format: {value}")