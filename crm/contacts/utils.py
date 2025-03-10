from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Q

def get_filtered_users(query):
    """
    Utility function to filter users by username, email, or name.
    """
    return User.objects.filter(
        Q(username__icontains=query) | 
        Q(email__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    )


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