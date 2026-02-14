"""Data processor."""
def transform(items):
    return [x.upper() for x in items if x]