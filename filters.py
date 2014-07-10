import time
import babel.dates

def format_timedelta(ts):
    """
    Transform a timestamp into a time delta (8 minutes ago, etc).
    This is a Jinja2 filter.
    """
    return babel.dates.format_timedelta(time.time() - ts)

def format_number(number, _format, **kwargs):
    """
    Format a number, with optional keywords and plural formatting.
    """
    if number == 1 and 'plural' in kwargs:
        kwargs['plural'] = ''
    return _format.format(number=number, **kwargs)

def pagination_range(page, page_count):
    """
    Determine which pages to show links for for pagination.
    This is a Jinja2 filter.
    """
    # Get the default set.
    pages = [1, 2, page - 2, page - 1, page, page + 1, page + 2, page_count - 1, page_count]

    # Filter out pages that are out of range.
    pages = [p for p in pages if p > 0 and p <= page_count]

    # Make sure everything is an int.
    pages = [int(p) for p in pages]

    # Remove duplicates.
    pages = set(pages)

    # Sort.
    pages = sorted(pages)

    return pages

FILTERS = (format_timedelta, format_number, pagination_range)
