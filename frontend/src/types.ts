export type WeatherCondition = "sunny" | "cloudy" | "rainy" | "partly-cloudy";

export interface FlightLeg {
  airline: string;
  flightNumber: string;
  departureAirport: string;
  departureTime: string; // ISO 8601
  arrivalAirport: string;
  arrivalTime: string; // ISO 8601
  cost: number; // USD per person
}

export interface Flights {
  outbound: FlightLeg;
  return: FlightLeg;
}

export interface Activity {
  id: string;
  name: string;
  cost: number;
  lat: number;
  lng: number;
}

export interface DayPeriod {
  activities: [Activity, Activity];
}

export interface DayPlan {
  dayNumber: number;
  date: string;
  weather: WeatherCondition;
  morning: DayPeriod;
  afternoon: DayPeriod;
  evening: DayPeriod;
}

export interface CategoryRating {
  category: string;
  stars: number; // 1–5
}

export interface TripPlan {
  destination: string;
  flights: Flights;
  packingList: { items: string[] };
  itinerary: DayPlan[];
  ratings: CategoryRating[];
}

// Maps activity id → locked boolean (UI-only, not from API)
export type LockState = Record<string, boolean>;
