import type { MenuItem } from "../types";
import apiClient from "./client";

// ── Enrichment layer ──────────────────────────────────────────────────────────
// The backend MenuItem model has no `category` or `imageUrl` fields.
// We store those client-side in localStorage keyed by item ID, and merge them
// on read. When the backend eventually gains these fields, this layer can be
// removed and the mappers updated.

const ENRICHMENT_KEY = "vendor_menu_enrichment_v1";

interface Enrichment {
  category: string;
  imageUrl: string;
}

function loadEnrichment(): Record<string, Enrichment> {
  try {
    return JSON.parse(localStorage.getItem(ENRICHMENT_KEY) ?? "{}") as Record<string, Enrichment>;
  } catch {
    return {};
  }
}

function saveEnrichment(map: Record<string, Enrichment>): void {
  localStorage.setItem(ENRICHMENT_KEY, JSON.stringify(map));
}

function setItemEnrichment(id: string, data: Enrichment): void {
  const map = loadEnrichment();
  map[id] = data;
  saveEnrichment(map);
}

function removeItemEnrichment(id: string): void {
  const map = loadEnrichment();
  delete map[id];
  saveEnrichment(map);
}

// ── Raw shapes from the backend ───────────────────────────────────────────────

interface RawMenuItem {
  id: number;
  vendor: number;
  name: string;
  description: string;
  price: string;
  is_available: boolean;
  prep_time_minutes: number;
}

// ── Mapper ────────────────────────────────────────────────────────────────────

function mapItem(raw: RawMenuItem, enrichment: Record<string, Enrichment>): MenuItem {
  const id = String(raw.id);
  const e = enrichment[id] ?? { category: "", imageUrl: "" };
  return {
    id,
    name: raw.name,
    description: raw.description,
    price: parseFloat(raw.price),
    isAvailable: raw.is_available,
    prepTimeMins: raw.prep_time_minutes,
    category: e.category,
    imageUrl: e.imageUrl,
  };
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function fetchMenuItems(): Promise<MenuItem[]> {
  const { data } = await apiClient.get<RawMenuItem[]>("/api/menu/items/");
  const enrichment = loadEnrichment();
  return data.map((raw) => mapItem(raw, enrichment));
}

export interface MenuItemFormData {
  vendorId: number;
  name: string;
  description: string;
  price: number;
  isAvailable: boolean;
  prepTimeMins: number;
  category: string;
  imageUrl: string;
}

export async function createMenuItem(form: MenuItemFormData): Promise<MenuItem> {
  const { data } = await apiClient.post<RawMenuItem>("/api/menu/items/", {
    vendor: form.vendorId,
    name: form.name,
    description: form.description,
    price: form.price,
    is_available: form.isAvailable,
    prep_time_minutes: form.prepTimeMins,
  });
  const id = String(data.id);
  setItemEnrichment(id, { category: form.category, imageUrl: form.imageUrl });
  return mapItem(data, loadEnrichment());
}

export async function updateMenuItem(id: string, form: Partial<MenuItemFormData>): Promise<MenuItem> {
  const body: Record<string, unknown> = {};
  if (form.name !== undefined) body.name = form.name;
  if (form.description !== undefined) body.description = form.description;
  if (form.price !== undefined) body.price = form.price;
  if (form.isAvailable !== undefined) body.is_available = form.isAvailable;
  if (form.prepTimeMins !== undefined) body.prep_time_minutes = form.prepTimeMins;

  const { data } = await apiClient.patch<RawMenuItem>(`/api/menu/items/${id}/`, body);

  // Always update enrichment fields if provided
  if (form.category !== undefined || form.imageUrl !== undefined) {
    const existing = loadEnrichment()[id] ?? { category: "", imageUrl: "" };
    setItemEnrichment(id, {
      category: form.category ?? existing.category,
      imageUrl: form.imageUrl ?? existing.imageUrl,
    });
  }

  return mapItem(data, loadEnrichment());
}

export async function deleteMenuItem(id: string): Promise<void> {
  await apiClient.delete(`/api/menu/items/${id}/`);
  removeItemEnrichment(id);
}

// ── Vendor helper ─────────────────────────────────────────────────────────────
// Returns the first vendor managed by the authenticated user. Temporary until
// a proper vendor-context endpoint is available (Phase 5).

interface RawVendor {
  id: number;
  name: string;
  location_label: string;
  is_active: boolean;
  intake_paused: boolean;
  manager: number | null;
}

export async function fetchMyVendorId(): Promise<number | null> {
  const { data } = await apiClient.get<RawVendor[]>("/api/vendors/");
  return data[0]?.id ?? null;
}
