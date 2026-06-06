# ML Data Directory

Downloaded datasets for CureDesk training and evaluation. Large files are gitignored; use the setup scripts to populate this tree locally.

## Quick start

```powershell
# Kaggle credentials required for most symptom/prescription Kaggle sets
# ~/.kaggle/kaggle.json or KAGGLE_USERNAME + KAGGLE_KEY

npm run setup:ml:data        # legacy: uom190346a + BD prescriptions
npm run setup:ml:data:all    # all recommended datasets (~500 MB)
npm run setup:ml:data:large  # includes large HF sets (~3–5 GB)
```

Inspect results:

```powershell
type ml\data\manifest.json
```

## Layout

| Path | Source | Notes |
|------|--------|-------|
| `symptoms/uom190346a/` | [Kaggle uom190346a](https://www.kaggle.com/datasets/uom190346a/disease-symptoms-and-patient-profile-dataset) | Current production CSV (349 rows) |
| `symptoms/itachi9604/` | [Kaggle itachi9604](https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset) | 4,920 rows, 132 symptoms |
| `symptoms/kaushil268/` | [Kaggle kaushil268](https://www.kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning) | Binarized ML features |
| `symptoms/niyarrbarman/` | [Kaggle niyarrbarman](https://www.kaggle.com/datasets/niyarrbarman/symptom2disease) | Symptom2Disease |
| `symptoms/nautiyalayush/` | [Kaggle nautiyalayush](https://www.kaggle.com/datasets/nautiyalayush/disease-prediction-using-symptoms) | 391 diseases |
| `symptoms/huggingface/diseases_consolidated/` | [HF kamruzzaman-asif/Diseases_Dataset](https://huggingface.co/datasets/kamruzzaman-asif/Diseases_Dataset) | All splits exported as CSV |
| `prescriptions/bd_handwritten/` | [Kaggle mamun1113](https://www.kaggle.com/datasets/mamun1113/doctors-handwritten-prescription-bd-dataset) | 780 BD images |
| `prescriptions/rxhandbd/` | [Mendeley 10.17632/dsb5r6vskg.3](https://data.mendeley.com/datasets/dsb5r6vskg/3) | RxHandBD |
| `prescriptions/hf_chinmays18/` | [HF chinmays18/medical-prescription-dataset](https://huggingface.co/datasets/chinmays18/medical-prescription-dataset) | ~1k images |
| `prescriptions/hf_handwritten_words/` | [HF avi-kai/Medical_Prescription_Handwritten_Words](https://huggingface.co/datasets/avi-kai/Medical_Prescription_Handwritten_Words) | Optional |
| `prescriptions/hf_african_medical/` | [HF African-Medical-Records](https://huggingface.co/datasets/Nigeria-Health-data-OCR-pipeline/African-Medical-Records) | Optional |
| `prescriptions/kaggle_illegible/` | [Kaggle mehaksingal](https://www.kaggle.com/datasets/mehaksingal/illegible-medical-prescription-images-dataset) | Optional |
| `drugs/rxnorm_prescribable/` | [NLM RxNorm prescribable zip](https://www.nlm.nih.gov/research/umls/rxnorm/docs/prescribe.html) | No UMLS license required |
| `drugs/rxterms/` | [NLM RxTerms zip](https://lhncbc.nlm.nih.gov/RxTerms/) | Simplified drug names |
| `rag/medquad/` | [HF keivalya/MedQuad-MedicalQnADataset](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) | ~16k Q&A pairs |
| `rag/medical_qa_lavita/` | [HF lavita/medical-qa-datasets](https://huggingface.co/datasets/lavita/medical-qa-datasets) | Health subset by default |

Legacy paths used by current training/seed scripts:

- `symptoms/Disease_symptom_and_patient_profile_dataset.csv` — synced from `uom190346a/`
- `prescriptions/images/` — synced from `bd_handwritten/`
- `prescriptions/testing_labels.csv`, `validation_labels.csv` — tracked in git

## Manual fallback

If a download fails, retry a single dataset:

```powershell
python ml/scripts/download_all.py --id symptoms_itachi9604
python ml/scripts/download_all.py --id prescriptions_rxhandbd --force
```

**RxHandBD (Mendeley manual download):** save `RxHandBD-ML.zip` and `RxHandBD-Raw.zip` from
[the dataset page](https://data.mendeley.com/datasets/dsb5r6vskg/3), wait for the browser download
to finish (not `.crdownload`), then:

```powershell
python ml/scripts/download_all.py --import-rxhandbd RxHandBD-ML.zip RxHandBD-Raw.zip
```

Check `manifest.json` for `status`, `error`, and manual URLs.

## Licenses

Each dataset has its own license. Review the source page before redistribution or commercial use. NLM RxNorm/RxTerms are subject to [NLM terms](https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html).
