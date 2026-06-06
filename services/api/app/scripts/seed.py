"""Seed database from symptom CSV and prescription label CSVs."""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "services" / "api"))

from app.db.models import Disease, Drug, PatientProfile, SessionLocal


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("'", "")


def seed_diseases_from_csv(csv_path: Path, db, *, include_profiles: bool = True) -> None:
    if not csv_path.exists():
        print(f"Symptom CSV not found at {csv_path}, skipping disease seed")
        return

    disease_stats: dict[str, dict] = {}

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Disease", "").strip()
            if not name:
                continue
            if name not in disease_stats:
                disease_stats[name] = {
                    "count": 0,
                    "fever": 0,
                    "cough": 0,
                    "fatigue": 0,
                    "difficulty_breathing": 0,
                }
            stats = disease_stats[name]
            stats["count"] += 1
            for key, col in [
                ("fever", "Fever"),
                ("cough", "Cough"),
                ("fatigue", "Fatigue"),
                ("difficulty_breathing", "Difficulty Breathing"),
            ]:
                if row.get(col, "").strip().lower() == "yes":
                    stats[key] += 1

            disease = db.query(Disease).filter(Disease.name == name).first()
            if not disease:
                disease = Disease(
                    slug=slugify(name),
                    name=name,
                    description=f"Educational information about {name}. Not a medical diagnosis.",
                    common_symptoms={},
                )
                db.add(disease)
                db.flush()

            if include_profiles:

                def yn(col: str) -> bool:
                    return row.get(col, "").strip().lower() == "yes"

                bp = row.get("Blood Pressure", "Normal").strip().lower()
                chol = row.get("Cholesterol Level", "Normal").strip().lower()
                gender = row.get("Gender", "Male").strip().lower()

                profile = PatientProfile(
                    disease_id=disease.id,
                    fever=yn("Fever"),
                    cough=yn("Cough"),
                    fatigue=yn("Fatigue"),
                    difficulty_breathing=yn("Difficulty Breathing"),
                    age=int(row.get("Age", 0) or 0),
                    gender=gender,
                    blood_pressure=bp,
                    cholesterol_level=chol,
                )
                db.add(profile)

    for name, stats in disease_stats.items():
        disease = db.query(Disease).filter(Disease.name == name).first()
        if disease and stats["count"]:
            disease.common_symptoms = {
                k: round(v / stats["count"], 2)
                for k, v in stats.items()
                if k != "count"
            }

    db.commit()
    print(f"Seeded {len(disease_stats)} diseases from {csv_path}")


def seed_diseases_from_itachi(db) -> None:
    desc_path = ROOT / "ml" / "data" / "symptoms" / "itachi9604" / "symptom_Description.csv"
    if not desc_path.exists():
        print(f"Itachi descriptions not found at {desc_path}, skipping")
        return
    added = 0
    updated = 0
    with desc_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("Disease", "").strip()
            description = row.get("Description", "").strip()
            if not name:
                continue
            slug = slugify(name)
            disease = db.query(Disease).filter(Disease.name == name).first()
            if not disease:
                disease = db.query(Disease).filter(Disease.slug == slug).first()
            if not disease:
                disease = Disease(
                    slug=slug,
                    name=name,
                    description=description or f"Information about {name}.",
                    common_symptoms={},
                )
                db.add(disease)
                added += 1
            elif description and (
                not disease.description or "Educational information about" in disease.description
            ):
                disease.description = description
                updated += 1
            db.flush()
    db.commit()
    print(f"Itachi9604: {added} new diseases, {updated} descriptions updated")


def seed_drugs_from_csvs(csv_paths: list[Path], db) -> None:
    seen: set[tuple[str, str]] = set()
    added = 0
    for csv_path in csv_paths:
        if not csv_path.exists():
            print(f"Drug CSV not found at {csv_path}, skipping")
            continue
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                brand = row.get("MEDICINE_NAME", "").strip()
                generic = row.get("GENERIC_NAME", "").strip()
                if not brand or (brand, generic) in seen:
                    continue
                seen.add((brand, generic))
                exists = (
                    db.query(Drug)
                    .filter(Drug.brand_name == brand, Drug.generic_name == generic)
                    .first()
                )
                if not exists:
                    db.add(Drug(brand_name=brand, generic_name=generic))
                    added += 1
    db.commit()
    print(f"Seeded {len(seen)} unique drugs ({added} new) from {len(csv_paths)} CSV(s)")


def seed_drugs_from_rxterms(db, *, limit: int = 8000) -> None:
    rx_dir = ROOT / "ml" / "data" / "drugs" / "rxterms"
    txt_files = sorted(rx_dir.glob("RxTerms*.txt"))
    txt_files = [p for p in txt_files if "Ingredients" not in p.name and "Archive" not in p.name]
    if not txt_files:
        print("RxTerms file not found, skipping")
        return

    seen: set[tuple[str, str]] = set()
    added = 0
    with txt_files[0].open(encoding="utf-8") as f:
        header = f.readline().strip().split("|")
        idx = {name: i for i, name in enumerate(header)}
        for line in f:
            if added >= limit:
                break
            parts = line.strip().split("|")
            if len(parts) < len(header):
                continue
            tty = parts[idx["TTY"]]
            if tty not in ("SBD", "SCD", "BPCK", "GPCK"):
                continue
            if parts[idx.get("IS_RETIRED", -1)] if "IS_RETIRED" in idx else "":
                continue
            brand = (parts[idx["DISPLAY_NAME"]] if "DISPLAY_NAME" in idx else "").strip()
            generic = (parts[idx["FULL_GENERIC_NAME"]] if "FULL_GENERIC_NAME" in idx else "").strip()
            psn = (parts[idx["PSN"]] if "PSN" in idx else "").strip()
            if not brand:
                brand = psn or generic
            if not generic:
                generic = psn or brand
            if not brand:
                continue
            key = (brand[:255], generic[:255])
            if key in seen:
                continue
            seen.add(key)
            exists = (
                db.query(Drug)
                .filter(Drug.brand_name == key[0], Drug.generic_name == key[1])
                .first()
            )
            if not exists:
                db.add(Drug(brand_name=key[0], generic_name=key[1]))
                added += 1
    db.commit()
    print(f"RxTerms: {added} new drugs ({len(seen)} unique pairs scanned)")


def main() -> None:
    from app.db.migrate import run_migrations

    run_migrations()
    db = SessionLocal()
    try:
        symptom_csv = (
            ROOT / "ml" / "data" / "symptoms" / "Disease_symptom_and_patient_profile_dataset.csv"
        )
        rx_dir = ROOT / "ml" / "data" / "prescriptions"
        drug_csvs = [
            rx_dir / "testing_labels.csv",
            rx_dir / "validation_labels.csv",
        ]
        seed_diseases_from_csv(symptom_csv, db)
        seed_diseases_from_itachi(db)
        seed_drugs_from_csvs(drug_csvs, db)
        seed_drugs_from_rxterms(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
