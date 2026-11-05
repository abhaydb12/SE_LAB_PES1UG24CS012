import math

MAX_PETS = 10        # sensible business limits
MAX_MINS = 240


def parse_walk_schedule(schedule_spec):
    """Parse 'PETS-MINS-WEEKEND' (e.g. '2-30-YES'). Returns a summary string or an error message."""
    if not isinstance(schedule_spec, str):
        return "Error: schedule must be a string like '2-30-YES'"

    parts = schedule_spec.strip().split('-')
    if len(parts) != 3:
        return "Error: schedule must have exactly 3 parts: PETS-MINS-WEEKEND"
    pets_str, mins_str, weekend_str = (p.strip() for p in parts)

    # isdecimal() + isascii() rejects '', signs, spaces and Unicode digits like '²'
    if not (pets_str.isascii() and pets_str.isdecimal()):
        return "Error: number of pets must be a whole number"
    if not (mins_str.isascii() and mins_str.isdecimal()):
        return "Error: minutes must be a whole number"
    pets, mins = int(pets_str), int(mins_str)

    if not 1 <= pets <= MAX_PETS:
        return f"Error: number of pets must be between 1 and {MAX_PETS}"
    if not 1 <= mins <= MAX_MINS:
        return f"Error: minutes must be between 1 and {MAX_MINS}"

    weekend_map = {"YES": 15.0, "NO": 0.0}
    weekend_fee = weekend_map.get(weekend_str.upper())
    if weekend_fee is None:
        return "Error: weekend flag must be YES or NO"

    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + (pets * 5.0) + weekend_fee
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"


def compute_pace_per_pet(walk_metrics_str):
    """Parse 'MINS/PETS' (e.g. '45/3'). Returns pace rounded to 2 dp, or None if input is invalid."""
    if not isinstance(walk_metrics_str, str):
        return None

    parts = walk_metrics_str.split('/')
    if len(parts) != 2:
        return None

    try:
        mins = float(parts[0])
        pets = float(parts[1])
    except ValueError:
        return None

    # reject nan / inf, negatives, zero pets and fractional pets
    if not (math.isfinite(mins) and math.isfinite(pets)):
        return None
    if mins < 0 or pets <= 0 or not pets.is_integer():
        return None

    pace = mins / pets
    if not math.isfinite(pace):
        return None
    return round(pace, 2)


def lookup_temperament_surcharge(temperament_code):
    """Return the surcharge for a temperament code (CALM, PLAYFUL, REACTIVE, AGGRESSIVE), or None if unknown."""
    if not isinstance(temperament_code, str):
        return None

    code = temperament_code.strip().upper()
    surcharges = {
        "CAL": 0.0,
        "PLY": 5.0,
        "REA": 12.0,
        "AGG": 20.0
    }
    # Original bug: 'PLAYFUL'[:3] is 'PLA', which never matched 'PLY'.
    # Accept the full names and the short codes.
    full_names = {"CALM": "CAL", "PLAYFUL": "PLY", "REACTIVE": "REA", "AGGRESSIVE": "AGG"}
    for name, key in full_names.items():
        if code == key or (len(code) >= 3 and name.startswith(code)):
            return surcharges[key]
    return None


def main():
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    print(parse_walk_schedule(s_input))

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    pace = compute_pace_per_pet(p_input)
    print("Pace (min/pet):", pace if pace is not None else "Error: enter MINUTES/PETS with pets > 0")

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    surcharge = lookup_temperament_surcharge(t_input)
    print("Surcharge: $", surcharge if surcharge is not None else "Error: unknown temperament code")


if __name__ == "__main__":
    main()
