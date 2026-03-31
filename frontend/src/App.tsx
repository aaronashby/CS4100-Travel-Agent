import { useState } from "react";
import "./App.css";
import axios from "axios";
import TripResult from "./TripResult";
import type { TripPlan } from "./types";

const ACTIVITY_OPTIONS = [
  "Museums",
  "Outdoors",
  "Food & Drink",
  "Shopping",
  "Nightlife",
  "Relaxation",
];

function Badge({
  label,
  selected,
  onClick,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "6px 14px",
        borderRadius: "999px",
        border: `1.5px solid ${selected ? "#4f8ef7" : "#ccc"}`,
        background: selected ? "#e8f0fe" : "#fff",
        color: selected ? "#1a56db" : "#555",
        cursor: "pointer",
        fontSize: "0.85rem",
        fontWeight: selected ? 600 : 400,
        transition: "all 0.15s",
      }}
    >
      {label}
    </button>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "#333" }}>
        {label} {required && <span style={{ color: "#e53e3e" }}>*</span>}
      </label>
      {children}
    </div>
  );
}

const inputStyle = {
  padding: "9px 12px",
  borderRadius: 8,
  border: "1.5px solid #ddd",
  fontSize: "0.95rem",
  outline: "none",
  width: "100%",
  boxSizing: "border-box" as const,
  color: "#222",
};

export default function App() {
  const [form, setForm] = useState({
    destination: "",
    startDate: "",
    endDate: "",
    budget: "",
    travelers: "",
    activities: [] as string[],
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [tripPlan, setTripPlan] = useState<TripPlan | null>(null);

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const toggleActivity = (a: string) =>
    setForm((f) => ({
      ...f,
      activities: f.activities.includes(a)
        ? f.activities.filter((x) => x !== a)
        : [...f.activities, a],
    }));

  const validateDays = () => {
    if (!form.startDate)
      return {
        isValid: false,
        startDateError: "Start date is required.",
        endDateError: "",
      };

    if (!form.endDate)
      return {
        isValid: false,
        startDateError: "",
        endDateError: "End date is required.",
      };

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const startDate = new Date(form.startDate);
    const endDate = new Date(form.endDate);

    if (startDate < today)
      return {
        isValid: false,
        startDateError: "Start date cannot be before today.",
        endDateError: "",
      };

    if (form.startDate && form.endDate && form.endDate < form.startDate)
      return {
        isValid: false,
        startDateError: "",
        endDateError: "End date must be after start date.",
      };

    const startDateMs = startDate.valueOf();
    const endDateMs = endDate.valueOf();

    const tripDurationMs = endDateMs - startDateMs;
    const durationNowToEndMs = endDateMs - Date.now().valueOf();
    const millisecondsPerDay = 1000 * 60 * 60 * 24;

    const durationNowToEndDays = Math.round(
      durationNowToEndMs / millisecondsPerDay,
    );

    if (durationNowToEndDays > 16)
      return {
        isValid: false,
        startDateError: "",
        endDateError: "End date must be at most 16 days from now",
      };

    const tripDurationDays = Math.round(tripDurationMs / millisecondsPerDay);

    if (tripDurationDays > 14)
      return {
        isValid: false,
        startDateError: "",
        endDateError: "Trip duration must be at most 14 days",
      };

    return { isValid: true, startDateError: "", endDateError: "" };
  };

  const validate = () => {
    const e: Record<string, string> = {};
    const dateValidationResult = validateDays();

    if (!dateValidationResult.isValid) {
      if (dateValidationResult.startDateError) {
        e.startDate = dateValidationResult.startDateError;
      }
      if (dateValidationResult.endDateError) {
        e.endDate = dateValidationResult.endDateError;
      }
    }

    if (!form.destination && form.activities.length === 0)
      e.destination =
        "Provide a destination or at least one activity preference.";
    if (!form.budget || parseInt(form.budget) <= 0)
      e.budget = "Budget must be a positive number";
    if (!form.travelers || parseInt(form.travelers) <= 0)
      e.travelers = "Number of travelers must be positive";
    return e;
  };

  const handleSubmit = async () => {
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length === 0) {
      try {
        const response = await axios.post(
          "http://localhost:5001/api/plan",
          form,
        );
        console.log("Plan Trip Response:", response.data);
        // TODO: when backend returns full plan: setTripPlan(response.data.plan);
        setTripPlan(null); // falls back to mock data in TripResult
        setSubmitted(true);
      } catch (error) {
        console.error("Error planning trip:", error);
      }
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setTripPlan(null);
    setForm({ destination: "", startDate: "", endDate: "", budget: "", travelers: "", activities: [] });
    setErrors({});
  };

  if (submitted) {
    return <TripResult plan={tripPlan} formData={form} onReset={handleReset} />;
  }

  return (
    <div
      style={{
        maxWidth: 500,
        margin: "60px auto",
        fontFamily: "system-ui, sans-serif",
        padding: "0 16px",
      }}
    >
      <div style={{ marginBottom: 28 }}>
        <h1
          style={{
            fontSize: "1.6rem",
            fontWeight: 700,
            color: "#111",
            margin: 0,
          }}
        >
          ✈️ Travel Planner
        </h1>
        <p style={{ color: "#666", marginTop: 6, fontSize: "0.9rem" }}>
          Tell us about your trip and we'll handle the rest.
        </p>
      </div>

      <div
        style={{
          background: "#fff",
          borderRadius: 16,
          border: "1px solid #e5e7eb",
          padding: "28px 24px",
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        {/* Destination */}
        <Field label="Destination">
          <input
            style={{
              ...inputStyle,
              borderColor: errors.destination ? "#e53e3e" : "#ddd",
            }}
            placeholder="e.g. Tokyo, Japan"
            value={form.destination}
            onChange={(e) => set("destination", e.target.value)}
          />
          {errors.destination && (
            <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>
              {errors.destination}
            </span>
          )}
        </Field>

        {/* Dates */}
        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}
        >
          <Field label="Start Date" required>
            <input
              type="date"
              style={{
                ...inputStyle,
                borderColor: errors.startDate ? "#e53e3e" : "#ddd",
              }}
              value={form.startDate}
              onChange={(e) => set("startDate", e.target.value)}
            />
            {errors.startDate && (
              <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>
                {errors.startDate}
              </span>
            )}
          </Field>
          <Field label="End Date" required>
            <input
              type="date"
              style={{
                ...inputStyle,
                borderColor: errors.endDate ? "#e53e3e" : "#ddd",
              }}
              value={form.endDate}
              onChange={(e) => set("endDate", e.target.value)}
            />
            {errors.endDate && (
              <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>
                {errors.endDate}
              </span>
            )}
          </Field>
        </div>

        {/* Budget + Travelers */}
        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}
        >
          <Field label="Budget (USD)">
            <input
              type="number"
              style={inputStyle}
              placeholder="e.g. 2000"
              value={form.budget}
              onChange={(e) => set("budget", e.target.value)}
            />
          </Field>
          <Field label="# of Travelers">
            <input
              type="number"
              style={inputStyle}
              placeholder="e.g. 2"
              min={1}
              value={form.travelers}
              onChange={(e) => set("travelers", e.target.value)}
            />
          </Field>
        </div>

        {/* Activity Preferences */}
        <Field label="Activity Preferences">
          <div
            style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 2 }}
          >
            {ACTIVITY_OPTIONS.map((a) => (
              <Badge
                key={a}
                label={a}
                selected={form.activities.includes(a)}
                onClick={() => toggleActivity(a)}
              />
            ))}
          </div>
        </Field>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          style={{
            marginTop: 4,
            padding: "11px",
            borderRadius: 10,
            border: "none",
            background: "#4f8ef7",
            color: "#fff",
            fontWeight: 700,
            fontSize: "1rem",
            cursor: "pointer",
          }}
        >
          Plan My Trip →
        </button>
      </div>
    </div>
  );
}
