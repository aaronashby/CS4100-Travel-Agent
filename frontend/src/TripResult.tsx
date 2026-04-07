import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import type {
  TripPlan,
  FlightLeg,
  Activity,
  DayPlan,
  CategoryRating,
  WeatherCondition,
  LockState,
} from "./types";

delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// ─── Mock Data ───────────────────────────────────────────────────────────────

const MOCK_PLAN: TripPlan = {
  destination: "Tokyo, Japan",
  flights: {
    outbound: {
      airline: "Japan Airlines",
      flightNumber: "JL 007",
      departureAirport: "BOS",
      departureTime: "2026-06-01T10:15:00",
      arrivalAirport: "NRT",
      arrivalTime: "2026-06-02T14:30:00",
      cost: 820,
    },
    return: {
      airline: "Japan Airlines",
      flightNumber: "JL 008",
      departureAirport: "NRT",
      departureTime: "2026-06-08T16:00:00",
      arrivalAirport: "BOS",
      arrivalTime: "2026-06-09T18:45:00",
      cost: 810,
    },
  },
  packingList: {
    items: [
      "Undergarments",
      "3 t-shirts",
      "2 pants",
      "2 hoodies/sweatshirts",
      "Umbrella",
      "Coat/Jacket",
      "Comfortable walking shoes",
      "Phone charger & adapter",
    ],
  },
  itinerary: [
    {
      dayNumber: 1,
      date: "2026-06-02",
      weather: "sunny",
      morning: {
        activities: [
          { id: "d1-m1", name: "Senso-ji Temple", cost: 0, lat: 35.7148, lng: 139.7967 },
          { id: "d1-m2", name: "Nakamise Shopping Street", cost: 30, lat: 35.7128, lng: 139.796 },
        ],
      },
      afternoon: {
        activities: [
          { id: "d1-a1", name: "teamLab Borderless", cost: 32, lat: 35.6257, lng: 139.7849 },
          { id: "d1-a2", name: "Odaiba Seaside Park", cost: 0, lat: 35.6267, lng: 139.775 },
        ],
      },
      evening: {
        activities: [
          { id: "d1-e1", name: "Shibuya Crossing & dinner", cost: 25, lat: 35.6595, lng: 139.7004 },
          { id: "d1-e2", name: "Shibuya Sky rooftop bar", cost: 20, lat: 35.658, lng: 139.7016 },
        ],
      },
    },
    {
      dayNumber: 2,
      date: "2026-06-03",
      weather: "partly-cloudy",
      morning: {
        activities: [
          { id: "d2-m1", name: "Tsukiji Outer Market", cost: 15, lat: 35.6654, lng: 139.7707 },
          { id: "d2-m2", name: "Hamarikyu Gardens", cost: 3, lat: 35.6602, lng: 139.7636 },
        ],
      },
      afternoon: {
        activities: [
          { id: "d2-a1", name: "Tokyo National Museum", cost: 10, lat: 35.7188, lng: 139.7762 },
          { id: "d2-a2", name: "Ueno Park stroll", cost: 0, lat: 35.7158, lng: 139.7743 },
        ],
      },
      evening: {
        activities: [
          { id: "d2-e1", name: "Ramen tasting in Shinjuku", cost: 18, lat: 35.6938, lng: 139.7036 },
          { id: "d2-e2", name: "Golden Gai bar crawl", cost: 30, lat: 35.694, lng: 139.702 },
        ],
      },
    },
    {
      dayNumber: 3,
      date: "2026-06-04",
      weather: "rainy",
      morning: {
        activities: [
          { id: "d3-m1", name: "Meiji Jingu Shrine", cost: 0, lat: 35.6764, lng: 139.6993 },
          { id: "d3-m2", name: "Harajuku Takeshita Street", cost: 20, lat: 35.6702, lng: 139.7027 },
        ],
      },
      afternoon: {
        activities: [
          { id: "d3-a1", name: "Mori Art Museum", cost: 18, lat: 35.6604, lng: 139.7292 },
          { id: "d3-a2", name: "Roppongi Hills tour", cost: 0, lat: 35.6605, lng: 139.7295 },
        ],
      },
      evening: {
        activities: [
          { id: "d3-e1", name: "Sushi dinner at Tsukiji", cost: 60, lat: 35.6659, lng: 139.7706 },
          { id: "d3-e2", name: "Tokyo Tower night view", cost: 12, lat: 35.6586, lng: 139.7454 },
        ],
      },
    },
  ],
  ratings: [
    { category: "Museums", stars: 4 },
    { category: "Food & Drink", stars: 4 },
    { category: "Outdoors", stars: 5 },
    { category: "Nightlife", stars: 4 },
    { category: "Flights", stars: 3 },
  ],
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function weatherLabel(condition: WeatherCondition): string {
  const map: Record<WeatherCondition, string> = {
    sunny: "Sunny",
    "partly-cloudy": "Partly Cloudy",
    cloudy: "Cloudy",
    rainy: "Rainy",
  };
  return map[condition];
}

function renderStars(n: number): string {
  const full = Math.round(n);
  return "★".repeat(full) + "☆".repeat(5 - full);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function FlightCard({ leg, label }: { leg: FlightLeg; label: string }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          fontSize: "0.75rem",
          fontWeight: 700,
          color: "#888",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          marginBottom: 4,
        }}
      >
        {label}
      </div>
      <div style={{ fontWeight: 600, fontSize: "0.95rem", color: "#111", marginBottom: 2 }}>
        {leg.airline} · {leg.flightNumber}
      </div>
      <div style={{ fontSize: "0.85rem", color: "#555", marginBottom: 2 }}>
        {leg.departureAirport} {formatTime(leg.departureTime)} → {leg.arrivalAirport}{" "}
        {formatTime(leg.arrivalTime)}
      </div>
      <div style={{ fontSize: "0.85rem", color: "#4f8ef7", fontWeight: 600 }}>
        ${leg.cost} / person
      </div>
    </div>
  );
}

function ActivityRow({
  activity,
  locked,
  onToggle,
}: {
  activity: Activity;
  locked: boolean;
  onToggle: (id: string) => void;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "8px 10px",
        border: "1px solid #e5e7eb",
        marginBottom: 6,
        background: locked ? "#f0f4ff" : "#fafafa",
      }}
    >
      <span style={{ fontSize: "0.9rem", color: "#222", fontWeight: 500 }}>{activity.name}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
        <span style={{ fontSize: "0.85rem", color: "#555" }}>
          {activity.cost === 0 ? "Free" : `$${activity.cost}`}
        </span>
        <button
          onClick={() => onToggle(activity.id)}
          title={locked ? "Unlock activity" : "Lock activity"}
          style={{
            border: "1px solid #ccc",
            background: locked ? "#4f8ef7" : "#fff",
            color: locked ? "#fff" : "#555",
            cursor: "pointer",
            fontSize: "0.75rem",
            fontWeight: 600,
            padding: "2px 8px",
            letterSpacing: "0.03em",
          }}
        >
          {locked ? "LOCKED" : "LOCK"}
        </button>
      </div>
    </div>
  );
}

function DayMap({ day }: { day: DayPlan }) {
  const all: Activity[] = [
    ...day.morning.activities,
    ...day.afternoon.activities,
    ...day.evening.activities,
  ];
  const centerLat = all.reduce((s, a) => s + a.lat, 0) / all.length;
  const centerLng = all.reduce((s, a) => s + a.lng, 0) / all.length;

  return (
    <div
      style={{
        height: 280,
        overflow: "hidden",
        border: "1px solid #e5e7eb",
        position: "sticky",
        top: 16,
      }}
    >
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {all.map((activity) => (
          <Marker key={activity.id} position={[activity.lat, activity.lng]}>
            <Popup>
              {activity.name}
              <br />
              {activity.cost === 0 ? "Free" : `$${activity.cost}`}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

function DaySection({
  day,
  lockState,
  onToggle,
}: {
  day: DayPlan;
  lockState: LockState;
  onToggle: (id: string) => void;
}) {
  const periodLabel = (label: string) => (
    <div
      style={{
        fontSize: "0.82rem",
        fontWeight: 700,
        color: "#666",
        marginTop: 14,
        marginBottom: 8,
        textTransform: "uppercase",
        letterSpacing: "0.04em",
      }}
    >
      {label}
    </div>
  );

  return (
    <div
      style={{
        background: "#fff",
        border: "1px solid #e5e7eb",
        padding: "20px 18px",
      }}
    >
      {/* Day header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 4,
          paddingBottom: 12,
          borderBottom: "1px solid #f0f0f0",
        }}
      >
        <span style={{ fontWeight: 700, fontSize: "1rem", color: "#111" }}>
          Day {day.dayNumber}
        </span>
        <span style={{ fontSize: "0.85rem", color: "#888" }}>{formatDate(day.date)}</span>
        <span style={{ marginLeft: "auto", fontSize: "0.8rem", color: "#888", textTransform: "uppercase", letterSpacing: "0.04em" }}>
          {weatherLabel(day.weather)}
        </span>
      </div>

      {periodLabel("Morning")}
      {day.morning.activities.map((a) => (
        <ActivityRow key={a.id} activity={a} locked={!!lockState[a.id]} onToggle={onToggle} />
      ))}

      {periodLabel("Afternoon")}
      {day.afternoon.activities.map((a) => (
        <ActivityRow key={a.id} activity={a} locked={!!lockState[a.id]} onToggle={onToggle} />
      ))}

      {periodLabel("Evening")}
      {day.evening.activities.map((a) => (
        <ActivityRow key={a.id} activity={a} locked={!!lockState[a.id]} onToggle={onToggle} />
      ))}
    </div>
  );
}

function RatingRow({ rating }: { rating: CategoryRating }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "8px 0",
        borderBottom: "1px solid #f0f0f0",
      }}
    >
      <span style={{ fontSize: "0.9rem", color: "#333", fontWeight: 500 }}>{rating.category}</span>
      <span style={{ fontSize: "1rem", color: "#f59e0b", letterSpacing: 2 }}>
        {renderStars(rating.stars)}
      </span>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

interface TripResultProps {
  plan: TripPlan | null;
  formData: {
    destination: string;
    startDate: string;
    endDate: string;
    budget: string;
    travelers: string;
    activities: string[];
  };
  onReset: () => void;
}

const cardStyle: React.CSSProperties = {
  background: "#fff",
  border: "1px solid #e5e7eb",
  padding: "20px 18px",
  marginBottom: 20,
};

export default function TripResult({ plan, formData, onReset }: TripResultProps) {
  const data = plan ?? MOCK_PLAN;
  const [lockState, setLockState] = useState<LockState>({});

  const toggleLock = (id: string) =>
    setLockState((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div
      style={{
        maxWidth: 1200,
        margin: "0 auto",
        padding: "24px 16px",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24,
          paddingBottom: 16,
          borderBottom: "1px solid #e5e7eb",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, color: "#111" }}>
            {formData.destination || data.destination}
          </h1>
          <p style={{ margin: "4px 0 0", fontSize: "0.9rem", color: "#666" }}>
            {formData.startDate} → {formData.endDate}
            {formData.travelers ? ` · ${formData.travelers} traveler${Number(formData.travelers) !== 1 ? "s" : ""}` : ""}
            {formData.budget ? ` · $${formData.budget} budget` : ""}
          </p>
        </div>
        <button
          onClick={onReset}
          style={{
            padding: "8px 16px",
            border: "1.5px solid #ddd",
            background: "#fff",
            color: "#444",
            fontWeight: 600,
            cursor: "pointer",
            fontSize: "0.85rem",
          }}
        >
          Plan Another Trip
        </button>
      </div>

      {/* Two-column layout */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "280px 1fr",
          gap: 24,
          alignItems: "start",
        }}
      >
        {/* Left sidebar */}
        <div>
          <div style={cardStyle}>
            <div
              style={{
                fontWeight: 700,
                fontSize: "1rem",
                color: "#111",
                marginBottom: 14,
                paddingBottom: 10,
                borderBottom: "1px solid #f0f0f0",
              }}
            >
              Flights
            </div>
            <FlightCard leg={data.flights.outbound} label="Outbound" />
            <FlightCard leg={data.flights.return} label="Return" />
          </div>

          <div style={cardStyle}>
            <div
              style={{
                fontWeight: 700,
                fontSize: "1rem",
                color: "#111",
                marginBottom: 12,
                paddingBottom: 10,
                borderBottom: "1px solid #f0f0f0",
              }}
            >
              Packing List
            </div>
            <ul style={{ margin: 0, paddingLeft: 18, display: "flex", flexDirection: "column", gap: 6 }}>
              {data.packingList.items.map((item) => (
                <li key={item} style={{ fontSize: "0.9rem", color: "#333" }}>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Main content */}
        <div>
          {data.itinerary.map((day) => (
            <div
              key={day.dayNumber}
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 320px",
                gap: 16,
                marginBottom: 28,
              }}
            >
              <DaySection day={day} lockState={lockState} onToggle={toggleLock} />
              <DayMap day={day} />
            </div>
          ))}

          <div style={{ ...cardStyle, marginBottom: 0 }}>
            <div
              style={{
                fontWeight: 700,
                fontSize: "1rem",
                color: "#111",
                marginBottom: 12,
                paddingBottom: 10,
                borderBottom: "1px solid #f0f0f0",
              }}
            >
              Ratings
            </div>
            {data.ratings.map((r) => (
              <RatingRow key={r.category} rating={r} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
