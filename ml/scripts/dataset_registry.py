"""Registry of external datasets for CureDesk ML data pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Group = Literal["symptoms", "prescriptions", "drugs", "rag"]
Method = Literal["kaggle", "hf", "mendeley", "nlm"]


@dataclass(frozen=True)
class DatasetEntry:
    id: str
    group: Group
    method: Method
    dest: str  # relative to ml/data/
    slug: str = ""
    url: str = ""
    doi: str = ""
    hf_config: str | None = None
    hf_splits: list[str] | None = None
    estimated_size_mb: int = 50
    license: str = "See source"
    requires_kaggle: bool = False
    large: bool = False
    optional: bool = False
    manual_url: str = ""


DATASETS: list[DatasetEntry] = [
    DatasetEntry(
        id="symptoms_uom190346a",
        group="symptoms",
        method="kaggle",
        slug="uom190346a/disease-symptoms-and-patient-profile-dataset",
        dest="symptoms/uom190346a",
        estimated_size_mb=1,
        license="Kaggle / see dataset page",
        requires_kaggle=True,
    ),
    DatasetEntry(
        id="symptoms_itachi9604",
        group="symptoms",
        method="kaggle",
        slug="itachi9604/disease-symptom-description-dataset",
        dest="symptoms/itachi9604",
        estimated_size_mb=2,
        license="GPL-3.0 (see Kaggle)",
        requires_kaggle=True,
    ),
    DatasetEntry(
        id="symptoms_kaushil268",
        group="symptoms",
        method="kaggle",
        slug="kaushil268/disease-prediction-using-machine-learning",
        dest="symptoms/kaushil268",
        estimated_size_mb=2,
        license="Kaggle / see dataset page",
        requires_kaggle=True,
    ),
    DatasetEntry(
        id="symptoms_niyarrbarman",
        group="symptoms",
        method="kaggle",
        slug="niyarrbarman/symptom2disease",
        dest="symptoms/niyarrbarman",
        estimated_size_mb=1,
        license="Kaggle / see dataset page",
        requires_kaggle=True,
    ),
    DatasetEntry(
        id="symptoms_nautiyalayush",
        group="symptoms",
        method="kaggle",
        slug="nautiyalayush/disease-prediction-using-symptoms",
        dest="symptoms/nautiyalayush",
        estimated_size_mb=2,
        license="Kaggle / see dataset page",
        requires_kaggle=True,
    ),
    DatasetEntry(
        id="symptoms_hf_consolidated",
        group="symptoms",
        method="hf",
        slug="kamruzzaman-asif/Diseases_Dataset",
        dest="symptoms/huggingface/diseases_consolidated",
        estimated_size_mb=50,
        license="See Hugging Face dataset card",
    ),
    DatasetEntry(
        id="symptoms_hf_dhivyeshrk",
        group="symptoms",
        method="hf",
        slug="kamruzzaman-asif/Diseases_Dataset",
        dest="symptoms/huggingface/dhivyeshrk",
        hf_config="default",
        hf_splits=["dhivyeshrk"],
        estimated_size_mb=200,
        license="See Hugging Face dataset card",
        large=True,
    ),
    DatasetEntry(
        id="prescriptions_bd",
        group="prescriptions",
        method="kaggle",
        slug="mamun1113/doctors-handwritten-prescription-bd-dataset",
        dest="prescriptions/bd_handwritten",
        estimated_size_mb=25,
        license="Kaggle / see dataset page",
        requires_kaggle=True,
    ),
    DatasetEntry(
        id="prescriptions_rxhandbd",
        group="prescriptions",
        method="mendeley",
        doi="10.17632/dsb5r6vskg.3",
        dest="prescriptions/rxhandbd",
        estimated_size_mb=150,
        license="CC BY 4.0",
        manual_url="https://data.mendeley.com/datasets/dsb5r6vskg/3",
    ),
    DatasetEntry(
        id="prescriptions_hf_chinmays18",
        group="prescriptions",
        method="hf",
        slug="chinmays18/medical-prescription-dataset",
        dest="prescriptions/hf_chinmays18",
        estimated_size_mb=120,
        license="See Hugging Face dataset card",
    ),
    DatasetEntry(
        id="prescriptions_hf_words",
        group="prescriptions",
        method="hf",
        slug="avi-kai/Medical_Prescription_Handwritten_Words",
        dest="prescriptions/hf_handwritten_words",
        estimated_size_mb=50,
        license="See Hugging Face dataset card",
        optional=True,
    ),
    DatasetEntry(
        id="prescriptions_hf_amr",
        group="prescriptions",
        method="hf",
        slug="Nigeria-Health-data-OCR-pipeline/African-Medical-Records",
        dest="prescriptions/hf_african_medical",
        estimated_size_mb=100,
        license="See Hugging Face dataset card",
        optional=True,
    ),
    DatasetEntry(
        id="prescriptions_kaggle_illegible",
        group="prescriptions",
        method="kaggle",
        slug="mehaksingal/illegible-medical-prescription-images-dataset",
        dest="prescriptions/kaggle_illegible",
        estimated_size_mb=80,
        license="Kaggle / see dataset page",
        requires_kaggle=True,
        optional=True,
    ),
    DatasetEntry(
        id="drugs_rxnorm_prescribable",
        group="drugs",
        method="nlm",
        url="https://download.nlm.nih.gov/rxnorm/RxNorm_full_prescribe_current.zip",
        dest="drugs/rxnorm_prescribable",
        estimated_size_mb=80,
        license="NLM RxNorm Terms of Service (prescribable subset)",
    ),
    DatasetEntry(
        id="drugs_rxterms",
        group="drugs",
        method="nlm",
        url="https://data.lhncbc.nlm.nih.gov/public/rxterms/release/RxTerms_current.zip",
        dest="drugs/rxterms",
        estimated_size_mb=5,
        license="NLM / public domain US government work",
        optional=True,
    ),
    DatasetEntry(
        id="rag_medquad",
        group="rag",
        method="hf",
        slug="keivalya/MedQuad-MedicalQnADataset",
        dest="rag/medquad",
        estimated_size_mb=25,
        license="See Hugging Face dataset card",
    ),
    DatasetEntry(
        id="rag_medical_qa_lavita",
        group="rag",
        method="hf",
        slug="lavita/medical-qa-datasets",
        dest="rag/medical_qa_lavita",
        estimated_size_mb=150,
        license="See Hugging Face dataset card",
    ),
    DatasetEntry(
        id="rag_medical_qa_lavita_full",
        group="rag",
        method="hf",
        slug="lavita/medical-qa-datasets",
        dest="rag/medical_qa_lavita_full",
        estimated_size_mb=1400,
        license="See Hugging Face dataset card",
        large=True,
    ),
]


def get_dataset(dataset_id: str) -> DatasetEntry:
    for entry in DATASETS:
        if entry.id == dataset_id:
            return entry
    raise KeyError(dataset_id)


def datasets_for_group(group: Group, *, include_large: bool = False) -> list[DatasetEntry]:
    out: list[DatasetEntry] = []
    for entry in DATASETS:
        if entry.group != group:
            continue
        if entry.large and not include_large:
            continue
        if entry.id == "rag_medical_qa_lavita_full" and not include_large:
            continue
        if entry.id == "rag_medical_qa_lavita" and include_large:
            continue
        out.append(entry)
    return out


def all_datasets(*, include_large: bool = False) -> list[DatasetEntry]:
    groups: list[Group] = ["symptoms", "prescriptions", "drugs", "rag"]
    seen: set[str] = set()
    out: list[DatasetEntry] = []
    for group in groups:
        for entry in datasets_for_group(group, include_large=include_large):
            if entry.id not in seen:
                seen.add(entry.id)
                out.append(entry)
    return out
