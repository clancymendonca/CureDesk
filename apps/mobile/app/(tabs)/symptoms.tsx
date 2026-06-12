import { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  Switch,
  TextInput,
  Pressable,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import {
  MEDICAL_DISCLAIMER,
  SYMPTOM_FEATURES,
  theme,
  DiseaseSummary,
  advancedSymptomFeatures,
  buildSymptomsPayload,
  friendlyErrorMessage,
  humanizeSymptom,
} from "@curedesk/shared";
import { api } from "../../lib/api";
import { Link } from "expo-router";

export default function SymptomsScreen() {
  const [fever, setFever] = useState(false);
  const [cough, setCough] = useState(false);
  const [fatigue, setFatigue] = useState(false);
  const [difficultyBreathing, setDifficultyBreathing] = useState(false);
  const [age, setAge] = useState("30");
  const [gender, setGender] = useState<"male" | "female">("female");
  const [bloodPressure, setBloodPressure] = useState<"normal" | "high" | "low">("normal");
  const [cholesterol, setCholesterol] = useState<"normal" | "high">("normal");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{ disease: string; slug: string; probability: number }[] | null>(null);
  const [confidenceLevel, setConfidenceLevel] = useState<"high" | "medium" | "low" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [advancedSymptoms, setAdvancedSymptoms] = useState<Record<string, boolean>>({});
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [symptomSearch, setSymptomSearch] = useState("");
  const [diseases, setDiseases] = useState<DiseaseSummary[]>([]);
  const [allFeatures, setAllFeatures] = useState<readonly string[]>(SYMPTOM_FEATURES);

  const filteredAdvanced = advancedSymptomFeatures(symptomSearch, allFeatures);
  const advancedCount = Object.values(advancedSymptoms).filter(Boolean).length;

  useEffect(() => {
    let cancelled = false;
    api
      .getSymptomFeatures()
      .then((r) => {
        if (!cancelled && r.features.length) setAllFeatures(r.features);
      })
      .catch(() => {
        /* keep bundled fallback list */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const searchSeq = useRef(0);

  useEffect(() => {
    const seq = ++searchSeq.current;
    const t = setTimeout(() => {
      api
        .listDiseases(search || undefined)
        .then((r) => {
          // Drop stale responses so older searches can't overwrite newer ones.
          if (seq === searchSeq.current) setDiseases(r.items);
        })
        .catch(() => {
          if (seq === searchSeq.current) setDiseases([]);
        });
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  async function onSubmit() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.predictSymptoms({
        fever,
        cough,
        fatigue,
        difficulty_breathing: difficultyBreathing,
        age: Math.min(120, Math.max(0, parseInt(age, 10) || 0)),
        gender,
        blood_pressure: bloodPressure,
        cholesterol_level: cholesterol,
        symptoms: buildSymptomsPayload(advancedSymptoms),
      });
      setResults(res.predictions);
      setConfidenceLevel(res.confidence_level);
    } catch (e) {
      setError(friendlyErrorMessage(e, "Prediction failed. Please try again."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.disclaimer}>{MEDICAL_DISCLAIMER}</Text>

      <Row label="Fever" value={fever} onChange={setFever} />
      <Row label="Cough" value={cough} onChange={setCough} />
      <Row label="Fatigue" value={fatigue} onChange={setFatigue} />
      <Row label="Difficulty Breathing" value={difficultyBreathing} onChange={setDifficultyBreathing} />

      <Text style={styles.label}>Age</Text>
      <TextInput style={styles.input} value={age} onChangeText={setAge} keyboardType="numeric" />

      <Text style={styles.label}>Gender</Text>
      <View style={styles.row}>
        {(["female", "male"] as const).map((g) => (
          <Pressable
            key={g}
            style={[styles.chip, gender === g && styles.chipActive]}
            onPress={() => setGender(g)}
          >
            <Text style={gender === g ? styles.chipTextActive : styles.chipText}>
              {g === "male" ? "Male" : "Female"}
            </Text>
          </Pressable>
        ))}
      </View>

      <Text style={styles.label}>Blood Pressure</Text>
      <View style={styles.row}>
        {(["normal", "high", "low"] as const).map((bp) => (
          <Pressable
            key={bp}
            style={[styles.chip, bloodPressure === bp && styles.chipActive]}
            onPress={() => setBloodPressure(bp)}
          >
            <Text style={bloodPressure === bp ? styles.chipTextActive : styles.chipText}>
              {bp.charAt(0).toUpperCase() + bp.slice(1)}
            </Text>
          </Pressable>
        ))}
      </View>

      <Text style={styles.label}>Cholesterol Level</Text>
      <View style={styles.row}>
        {(["normal", "high"] as const).map((c) => (
          <Pressable
            key={c}
            style={[styles.chip, cholesterol === c && styles.chipActive]}
            onPress={() => setCholesterol(c)}
          >
            <Text style={cholesterol === c ? styles.chipTextActive : styles.chipText}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </Text>
          </Pressable>
        ))}
      </View>

      <Pressable style={styles.advancedToggle} onPress={() => setAdvancedOpen(!advancedOpen)}>
        <Text style={styles.advancedToggleText}>
          Advanced symptoms ({advancedCount} selected) {advancedOpen ? "−" : "+"}
        </Text>
      </Pressable>
      {advancedOpen && (
        <View style={styles.advancedBox}>
          <TextInput
            style={styles.input}
            placeholder="Search symptoms..."
            value={symptomSearch}
            onChangeText={setSymptomSearch}
          />
          <ScrollView style={styles.advancedList} nestedScrollEnabled>
            {filteredAdvanced.map((key) => (
              <Row
                key={key}
                label={humanizeSymptom(key)}
                value={!!advancedSymptoms[key]}
                onChange={(v) => setAdvancedSymptoms((prev) => ({ ...prev, [key]: v }))}
              />
            ))}
          </ScrollView>
        </View>
      )}

      <Pressable style={styles.button} onPress={onSubmit} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Get Predictions</Text>
        )}
      </Pressable>

      {error && <Text style={styles.error}>{error}</Text>}
      {results && (
        <View style={styles.results}>
          <Text style={styles.resultsTitle}>Top predictions</Text>
          {confidenceLevel === "low" && (
            <Text style={styles.lowConfidence}>
              Uncertain match — consult a clinician. Not a diagnosis.
            </Text>
          )}
          {confidenceLevel === "medium" && (
            <Text style={styles.mediumConfidence}>
              Moderate confidence — educational guidance only.
            </Text>
          )}
          {results.map((r) => (
            <Link key={r.disease} href={`/disease/${r.slug}`} asChild>
              <Pressable>
                <Text style={styles.resultItem}>
                  {r.disease}: {(r.probability * 100).toFixed(1)}%
                </Text>
              </Pressable>
            </Link>
          ))}
        </View>
      )}

      <Text style={styles.sectionTitle}>Browse diseases</Text>
      <TextInput
        style={styles.input}
        placeholder="Search diseases..."
        value={search}
        onChangeText={setSearch}
      />
      {diseases.map((d) => (
        <Link key={d.slug} href={`/disease/${d.slug}`} asChild>
          <Pressable>
            <Text style={styles.diseaseLink}>{d.name}</Text>
          </Pressable>
        </Link>
      ))}
    </ScrollView>
  );
}

function Row({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <View style={styles.switchRow}>
      <Text style={styles.label}>{label}</Text>
      <Switch value={value} onValueChange={onChange} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.background },
  content: { padding: 16, paddingBottom: 40 },
  disclaimer: { fontSize: 12, color: theme.textMuted, marginBottom: 16, lineHeight: 18 },
  label: { fontSize: 16, fontWeight: "600", color: theme.text, marginTop: 12 },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
    backgroundColor: "#fff",
  },
  row: { flexDirection: "row", gap: 8, marginTop: 8 },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: theme.primary,
  },
  chipActive: { backgroundColor: theme.primary },
  chipText: { color: theme.primary },
  chipTextActive: { color: "#fff" },
  switchRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 8 },
  advancedToggle: {
    marginTop: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    backgroundColor: "#f9fafb",
  },
  advancedToggleText: { fontWeight: "600", color: theme.text },
  advancedBox: {
    marginTop: 8,
    padding: 12,
    backgroundColor: "#fff",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#eee",
  },
  advancedList: { maxHeight: 280, marginTop: 4 },
  button: {
    backgroundColor: theme.primary,
    padding: 16,
    borderRadius: 24,
    alignItems: "center",
    marginTop: 24,
  },
  buttonText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  error: { color: theme.error, marginTop: 12 },
  results: { marginTop: 24, padding: 16, backgroundColor: "#fff", borderRadius: 12 },
  resultsTitle: { fontWeight: "700", marginBottom: 8 },
  lowConfidence: {
    fontSize: 12,
    color: "#92400e",
    backgroundColor: "#fffbeb",
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  mediumConfidence: {
    fontSize: 12,
    color: theme.textMuted,
    backgroundColor: "#f9fafb",
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  resultItem: { fontSize: 15, marginVertical: 4 },
  sectionTitle: { fontSize: 18, fontWeight: "700", marginTop: 24, marginBottom: 8 },
  diseaseLink: { fontSize: 15, color: theme.primary, marginVertical: 6 },
});
