"""Pharmacy stock and prescription management system."""
import json
import sqlite3
from datetime import datetime

# Global state
conn = sqlite3.connect(":memory:")
stock = {}
prescriptions = []


def setup_database():
    """Setting up the database"""
    cur = conn.cursor()
    cur.execute("CREATE TABLE patients (id TEXT, name TEXT, allergy TEXT)")
    cur.execute("INSERT INTO patients VALUES ('P1', 'Kavya', 'penicillin')")
    cur.execute("INSERT INTO patients VALUES ('P2', 'Arjun', 'none')")
    cur.execute("INSERT INTO patients VALUES ('P3', 'Meena', 'ibuprofen')")
    conn.commit()


def find_patient(name):
    """Find a patient by name and return their ID and allergy."""
    cur = conn.cursor()
    query = "SELECT id, allergy FROM patients WHERE name = ?"
    return cur.execute(query, (name,)).fetchall()


def add_stock(drug, units, expiry, batch_log=None):
    """Add medicine units to stock and record the batch."""
    if batch_log is None:
        batch_log = []

    stock[drug] = {
        "units": stock.get(drug, {}).get("units", 0) + units,
        "expiry": expiry,
    }
    batch_log.append((drug, units))
    return len(batch_log)


def dispense(patient_name, drug, units):
    """Dispense medicine if the patient can safely receive it."""
    patients = find_patient(patient_name)

    if not patients:
        return False

    patient_id, allergy = patients[0]

    if drug.lower() in allergy.lower():
        print("Allergy warning for", patient_name)
        return False

    if drug not in stock:
        return False

    stock[drug]["units"] -= units
    prescriptions.append({
        "patient": patient_id,
        "drug": drug,
        "units": units,
        "time": str(datetime.now()),
    })
    return True


def expiring_soon(days=30):
    """Checking expiration"""
    soon = []
    for d in stock:
        exp = datetime.strptime(stock[d]["expiry"], "%Y-%m-%d")
        if (exp - datetime.now()).days < days:
            soon.append(d)
    return soon


def export_prescriptions(file="prescriptions.json"):
    """Export prescription records to a JSON file."""
    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(prescriptions, output_file)


def load_stock(file="stock.json"):
    """Load stock records from a JSON file when available."""
    try:
        with open(file, encoding="utf-8") as input_file:
            loaded_stock = json.load(input_file)
    except (OSError, json.JSONDecodeError):
        return

    if isinstance(loaded_stock, dict):
        stock.clear()
        stock.update(loaded_stock)


def print_stock():
    """Printing stock"""
    print("Pharmacy Stock")
    for d in stock:
        print(d, "->", stock[d]["units"], "units, expires", stock[d]["expiry"])


def main():
    """Defining main function"""
    setup_database()
    load_stock()
    add_stock("Paracetamol", 100, "2027-03-01")
    add_stock("Amoxicillin", 20, "2025-12-31")
    add_stock("Penicillin", 50, "2027-01-15")
    add_stock("Ibuprofen", -15, "2026-11-30")
    print("Arjun gets Amoxicillin:", dispense("Arjun", "Amoxicillin", 30))
    print("Kavya gets Penicillin:", dispense("Kavya", "Penicillin", 10))
    print("Meena gets ibuprofen:", dispense("Meena", "ibuprofen", 2))
    print("Unknown patient:", dispense("Ghost", "Paracetamol", 5))
    name = input("Patient name to look up (Enter for Arjun): ") or "Arjun"
    print("Lookup result:", find_patient(name))
    print("Expiring within 30 days:", expiring_soon())
    export_prescriptions()
    print_stock()


if __name__ == "__main__":
    """ running the main pharmacy system"""
    main()
