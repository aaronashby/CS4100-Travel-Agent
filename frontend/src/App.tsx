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
  const [isLoading, setIsLoading] = useState(false);

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

    const [startYear, startMonth, startDay] = form.startDate.split("-").map(Number);
    const startDate = new Date(startYear, startMonth - 1, startDay);
    const [endYear, endMonth, endDay] = form.endDate.split("-").map(Number);
    const endDate = new Date(endYear, endMonth - 1, endDay);

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
    const millisecondsPerDay = 1000 * 60 * 60 * 24;
    
    // Removing 16 day limit so users can plan any time in the future

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
    if (form.budget && parseInt(form.budget) <= 0)
      e.budget = "Budget must be a positive number";
    if (form.travelers && parseInt(form.travelers) <= 0)
      e.travelers = "Number of travelers must be positive";
    return e;
  };

  const handleSubmit = async () => {
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length === 0) {
      setIsLoading(true);
      console.log("Submitting form:", form);
      try {
        const response = await axios.post(
          "http://127.0.0.1:5001/api/plan",
          form,
        );
        console.log("Plan Trip Response:", response.data);
        setTripPlan(response.data);
        setSubmitted(true);
      } catch (error) {
        console.error("Error planning trip:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setTripPlan(null);
    setForm({ destination: "", startDate: "", endDate: "", budget: "", travelers: "", activities: [] });
    setErrors({});
  };

  if (isLoading) {
    return (
      <div style={{
        height: "100dvh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "system-ui, sans-serif",
        gap: 20
      }}>
        <div style={{
          width: 40,
          height: 40,
          border: "4px solid #f3f3f3",
          borderTop: "4px solid #4f8ef7",
          borderRadius: "50%",
          animation: "spin 1s linear infinite"
        }} />
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        <div style={{ textAlign: "center" }}>
          <h2 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>Crafting your perfect trip...</h2>
          <p style={{ color: "#666", marginTop: 8 }}>Our AI is searching for the best spots and optimizing your plan.</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return <TripResult plan={tripPlan} formData={form} onReset={handleReset} />;
  }

  return (
    <div
      style={{
        minHeight: "100dvh",
        display: "flex",
        flexDirection: "column",
        fontFamily: "system-ui, sans-serif",
        padding: "5vw",
        boxSizing: "border-box",
        maxWidth: "800px",
        margin: "0 auto",
      }}
    >
      <div style={{ marginBottom: 32 }}>
        <h1
          style={{
            fontSize: "2.2rem",
            fontWeight: 800,
            color: "#111",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          Travel Planner
        </h1>
        <p style={{ color: "#666", marginTop: 8, fontSize: "1.05rem" }}>
          Tell us about your trip and we'll handle the rest.
        </p>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 24,
          flex: 1,
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
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}
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
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}
        >
          <Field label="Budget (USD)">
            <input
              type="number"
              style={{
                ...inputStyle,
                borderColor: errors.budget ? "#e53e3e" : "#ddd",
              }}
              placeholder="e.g. 2000"
              value={form.budget}
              onChange={(e) => set("budget", e.target.value)}
            />
            {errors.budget && (
              <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>
                {errors.budget}
              </span>
            )}
          </Field>
          <Field label="# of Travelers">
            <input
              type="number"
              style={{
                ...inputStyle,
                borderColor: errors.travelers ? "#e53e3e" : "#ddd",
              }}
              placeholder="e.g. 2"
              min={1}
              value={form.travelers}
              onChange={(e) => set("travelers", e.target.value)}
            />
            {errors.travelers && (
              <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>
                {errors.travelers}
              </span>
            )}
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
            marginTop: "auto",
            padding: "16px",
            borderRadius: 12,
            border: "none",
            background: "#4f8ef7",
            color: "#fff",
            fontWeight: 700,
            fontSize: "1.1rem",
            cursor: "pointer",
            width: "100%",
          }}
        >
          Plan My Trip →
        </button>
      </div>
    </div>
  );
}
