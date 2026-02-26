import { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const ACTIVITY_OPTIONS = ["Museums", "Outdoors", "Food & Drink", "Shopping", "Nightlife", "Relaxation"];

function Badge({ label, selected, onClick }: { label: string; selected: boolean; onClick: () => void }) {
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

function Field({ label, required, children }: { label: string; required?: boolean; children: React.ReactNode }) {
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

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const toggleActivity = (a: string) =>
    setForm(f => ({
      ...f,
      activities: f.activities.includes(a) ? f.activities.filter(x => x !== a) : [...f.activities, a],
    }));

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.startDate) e.startDate = "Start date is required.";
    if (!form.endDate) e.endDate = "End date is required.";
    if (form.startDate && form.endDate && form.endDate < form.startDate)
      e.endDate = "End date must be after start date.";
    if (!form.destination && form.activities.length === 0)
      e.destination = "Provide a destination or at least one activity preference.";
    return e;
  };

  const handleSubmit = async () => {
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length === 0) {
      try {
        const response = await axios.post("http://localhost:5001/api/plan", form);
        console.log("Plan Trip Response:", response.data);
        setSubmitted(true);
      } catch (error) {
        console.error("Error planning trip:", error);
      }
    }
  };

  const handleReset = () => {
    setSubmitted(false);
    setForm({ destination: "", startDate: "", endDate: "", budget: "", travelers: "", activities: [] });
    setErrors({});
  };

  if (submitted) {
    return (
      <div style={{ maxWidth: 500, margin: "60px auto", fontFamily: "system-ui, sans-serif", padding: "0 16px" }}>
        <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #e5e7eb", padding: "32px 28px" }}>
          <div style={{ fontSize: "1.5rem", marginBottom: 8 }}>✈️ Trip Submitted!</div>
          <p style={{ color: "#555", fontSize: "0.95rem", marginBottom: 20 }}>
            Here's what you entered. Soon this will trigger the backend to generate your itinerary.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, fontSize: "0.9rem", color: "#333" }}>
            {form.destination && <div><strong>Destination:</strong> {form.destination}</div>}
            <div><strong>Dates:</strong> {form.startDate} → {form.endDate}</div>
            {form.budget && <div><strong>Budget:</strong> ${form.budget}</div>}
            {form.travelers && <div><strong>Travelers:</strong> {form.travelers}</div>}
            {form.activities.length > 0 && <div><strong>Activities:</strong> {form.activities.join(", ")}</div>}
          </div>
          <button
            onClick={handleReset}
            style={{ marginTop: 24, padding: "10px 20px", borderRadius: 8, border: "none", background: "#4f8ef7", color: "#fff", fontWeight: 600, cursor: "pointer", fontSize: "0.9rem" }}
          >
            Plan Another Trip
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 500, margin: "60px auto", fontFamily: "system-ui, sans-serif", padding: "0 16px" }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: "1.6rem", fontWeight: 700, color: "#111", margin: 0 }}>✈️ Travel Planner</h1>
        <p style={{ color: "#666", marginTop: 6, fontSize: "0.9rem" }}>Tell us about your trip and we'll handle the rest.</p>
      </div>

      <div style={{ background: "#fff", borderRadius: 16, border: "1px solid #e5e7eb", padding: "28px 24px", display: "flex", flexDirection: "column", gap: 20 }}>

        {/* Destination */}
        <Field label="Destination">
          <input
            style={{ ...inputStyle, borderColor: errors.destination ? "#e53e3e" : "#ddd" }}
            placeholder="e.g. Tokyo, Japan"
            value={form.destination}
            onChange={e => set("destination", e.target.value)}
          />
          {errors.destination && <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>{errors.destination}</span>}
        </Field>

        {/* Dates */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <Field label="Start Date" required>
            <input
              type="date"
              style={{ ...inputStyle, borderColor: errors.startDate ? "#e53e3e" : "#ddd" }}
              value={form.startDate}
              onChange={e => set("startDate", e.target.value)}
            />
            {errors.startDate && <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>{errors.startDate}</span>}
          </Field>
          <Field label="End Date" required>
            <input
              type="date"
              style={{ ...inputStyle, borderColor: errors.endDate ? "#e53e3e" : "#ddd" }}
              value={form.endDate}
              onChange={e => set("endDate", e.target.value)}
            />
            {errors.endDate && <span style={{ color: "#e53e3e", fontSize: "0.8rem" }}>{errors.endDate}</span>}
          </Field>
        </div>

        {/* Budget + Travelers */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <Field label="Budget (USD)">
            <input
              type="number"
              style={inputStyle}
              placeholder="e.g. 2000"
              value={form.budget}
              onChange={e => set("budget", e.target.value)}
            />
          </Field>
          <Field label="# of Travelers">
            <input
              type="number"
              style={inputStyle}
              placeholder="e.g. 2"
              min={1}
              value={form.travelers}
              onChange={e => set("travelers", e.target.value)}
            />
          </Field>
        </div>

        {/* Activity Preferences */}
        <Field label="Activity Preferences">
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 2 }}>
            {ACTIVITY_OPTIONS.map(a => (
              <Badge key={a} label={a} selected={form.activities.includes(a)} onClick={() => toggleActivity(a)} />
            ))}
          </div>
        </Field>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          style={{ marginTop: 4, padding: "11px", borderRadius: 10, border: "none", background: "#4f8ef7", color: "#fff", fontWeight: 700, fontSize: "1rem", cursor: "pointer" }}
        >
          Plan My Trip →
        </button>
      </div>
    </div>
  );
}
