

def get_first_and_last_name(full_name):
    parts = full_name.split()

    first_name = parts[0].capitalize()

    if len(parts) > 1:
        last_name = parts[-1].capitalize()
        return f"{first_name} {last_name}"
    else:
        return first_name
