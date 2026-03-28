import { CountryData } from './store';

// Simple lat/lng to country mapping using bounding boxes
interface CountryBounds {
  name: string;
  region: string;
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
}

const COUNTRY_BOUNDS: CountryBounds[] = [
  { name: 'Turkey', region: 'Middle East', minLat: 35.8, maxLat: 42.1, minLng: 25.7, maxLng: 44.8 },
  { name: 'United States', region: 'North America', minLat: 24.5, maxLat: 49.4, minLng: -124.8, maxLng: -66.9 },
  { name: 'Russia', region: 'Eurasia', minLat: 41.2, maxLat: 81.9, minLng: 19.6, maxLng: 180.0 },
  { name: 'China', region: 'Asia', minLat: 18.2, maxLat: 53.6, minLng: 73.5, maxLng: 134.8 },
  { name: 'India', region: 'South Asia', minLat: 8.1, maxLat: 37.1, minLng: 68.1, maxLng: 97.4 },
  { name: 'Brazil', region: 'South America', minLat: -33.8, maxLat: 5.3, minLng: -73.9, maxLng: -34.7 },
  { name: 'Australia', region: 'Oceania', minLat: -43.6, maxLat: -10.7, minLng: 113.3, maxLng: 153.6 },
  { name: 'Germany', region: 'Europe', minLat: 47.3, maxLat: 55.1, minLng: 5.9, maxLng: 15.0 },
  { name: 'United Kingdom', region: 'Europe', minLat: 49.9, maxLat: 60.9, minLng: -8.6, maxLng: 1.8 },
  { name: 'France', region: 'Europe', minLat: 41.3, maxLat: 51.1, minLng: -5.1, maxLng: 9.6 },
  { name: 'Saudi Arabia', region: 'Middle East', minLat: 16.4, maxLat: 32.2, minLng: 34.5, maxLng: 55.7 },
  { name: 'Japan', region: 'East Asia', minLat: 24.3, maxLat: 45.5, minLng: 122.9, maxLng: 153.9 },
  { name: 'South Korea', region: 'East Asia', minLat: 33.1, maxLat: 38.6, minLng: 124.6, maxLng: 129.6 },
  { name: 'Canada', region: 'North America', minLat: 41.7, maxLat: 83.1, minLng: -141.0, maxLng: -52.6 },
  { name: 'Mexico', region: 'North America', minLat: 14.5, maxLat: 32.7, minLng: -117.1, maxLng: -86.7 },
  { name: 'Argentina', region: 'South America', minLat: -55.1, maxLat: -21.8, minLng: -73.6, maxLng: -53.6 },
  { name: 'South Africa', region: 'Africa', minLat: -34.8, maxLat: -22.1, minLng: 16.5, maxLng: 33.0 },
  { name: 'Egypt', region: 'Africa', minLat: 22.0, maxLat: 31.7, minLng: 24.7, maxLng: 36.9 },
  { name: 'Nigeria', region: 'Africa', minLat: 4.3, maxLat: 13.9, minLng: 2.7, maxLng: 14.7 },
  { name: 'Iran', region: 'Middle East', minLat: 25.1, maxLat: 39.8, minLng: 44.0, maxLng: 63.3 },
  { name: 'Pakistan', region: 'South Asia', minLat: 23.6, maxLat: 37.1, minLng: 60.9, maxLng: 77.8 },
  { name: 'Indonesia', region: 'Southeast Asia', minLat: -10.9, maxLat: 5.9, minLng: 95.0, maxLng: 141.0 },
  { name: 'Spain', region: 'Europe', minLat: 35.9, maxLat: 43.8, minLng: -9.3, maxLng: 4.3 },
  { name: 'Italy', region: 'Europe', minLat: 35.5, maxLat: 47.1, minLng: 6.6, maxLng: 18.5 },
  { name: 'Ukraine', region: 'Europe', minLat: 44.4, maxLat: 52.4, minLng: 22.1, maxLng: 40.2 },
  { name: 'Kazakhstan', region: 'Central Asia', minLat: 40.6, maxLat: 55.4, minLng: 50.3, maxLng: 87.4 },
  { name: 'Thailand', region: 'Southeast Asia', minLat: 5.6, maxLat: 20.5, minLng: 97.4, maxLng: 105.7 },
  { name: 'Poland', region: 'Europe', minLat: 49.0, maxLat: 54.8, minLng: 14.1, maxLng: 24.2 },
  { name: 'Sweden', region: 'Europe', minLat: 55.3, maxLat: 69.1, minLng: 10.9, maxLng: 24.2 },
  { name: 'Norway', region: 'Europe', minLat: 57.9, maxLat: 71.2, minLng: 4.6, maxLng: 31.1 },
  { name: 'Greenland', region: 'Arctic', minLat: 59.8, maxLat: 83.6, minLng: -73.0, maxLng: -12.1 },
  { name: 'Alaska', region: 'North America', minLat: 54.7, maxLat: 71.4, minLng: -168.0, maxLng: -130.0 },
];

// Convert 3D point on sphere to lat/lng
export function pointToLatLng(x: number, y: number, z: number): { lat: number; lng: number } {
  const lat = Math.asin(y) * (180 / Math.PI);
  const lng = Math.atan2(-z, x) * (180 / Math.PI);
  return { lat, lng };
}

// Detect country from lat/lng
export function detectCountry(lat: number, lng: number): CountryData {
  // Normalize longitude
  let normalizedLng = lng;
  while (normalizedLng > 180) normalizedLng -= 360;
  while (normalizedLng < -180) normalizedLng += 360;

  for (const country of COUNTRY_BOUNDS) {
    if (
      lat >= country.minLat && lat <= country.maxLat &&
      normalizedLng >= country.minLng && normalizedLng <= country.maxLng
    ) {
      return {
        name: country.name,
        region: country.region,
        lat: Math.round(lat * 100) / 100,
        lng: Math.round(normalizedLng * 100) / 100,
        signalStrength: Math.floor(Math.random() * 30) + 70,
        activeSatellites: Math.floor(Math.random() * 8) + 2,
      };
    }
  }

  // Default: Ocean / Unknown
  const oceanNames = ['Pacific Ocean', 'Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean', 'Southern Ocean'];
  const oceanName = lat > 60 ? 'Arctic Ocean' : lat < -55 ? 'Southern Ocean' :
    normalizedLng > -30 && normalizedLng < 20 ? 'Atlantic Ocean' :
    normalizedLng > 20 && normalizedLng < 100 ? 'Indian Ocean' : 'Pacific Ocean';

  return {
    name: oceanName,
    region: 'International Waters',
    lat: Math.round(lat * 100) / 100,
    lng: Math.round(normalizedLng * 100) / 100,
    signalStrength: Math.floor(Math.random() * 20) + 50,
    activeSatellites: Math.floor(Math.random() * 4) + 1,
  };
}
