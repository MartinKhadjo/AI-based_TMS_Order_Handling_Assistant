/*
 * Copyright (c) 2026 Martin Khadjavian. All rights reserved.
 * Website: https://martinkhadjavian.com
 */

export type Customer = {
  id: number;
  name: string;
  contact_email: string;
  company_type: string;
};

export type Vehicle = {
  id: number;
  vin: string;
  brand: string;
  model: string;
  length_m?: string | null;
  height_m?: string | null;
  weight_kg?: number | null;
  status: string;
  current_location: string;
};

export type TrackingEvent = {
  id: number;
  event_type: string;
  location: string;
  timestamp: string;
  description: string;
};

export type TransportOrder = {
  id: number;
  customer: number;
  customer_detail: Customer;
  vehicle: number;
  vehicle_detail: Vehicle;
  pickup_location: string;
  delivery_location: string;
  requested_pickup_date: string | null;
  requested_delivery_date: string | null;
  status: string;
  priority: string;
  notes: string;
  created_by_ai: boolean;
  tracking_events: TrackingEvent[];
  created_at: string;
};

export type Dashboard = {
  customers: number;
  vehicles: number;
  orders: number;
  open_orders: number;
  ai_created_orders: number;
  orders_by_status: Record<string, number>;
  vehicles_by_status: Record<string, number>;
};

export type DraftOrder = {
  customer_name: string | null;
  vehicle_brand: string | null;
  vehicle_model: string | null;
  vin: string | null;
  pickup_location: string | null;
  delivery_location: string | null;
  requested_pickup_date: string | null;
  requested_delivery_date: string | null;
  priority: string;
  notes: string;
};

export type ExtractionResponse = {
  draft: DraftOrder;
  missing_fields: string[];
  validation_errors: string[];
  warnings: string[];
  confidence: number;
  provider: string;
};

export type ToolQueryResponse = {
  tool: string;
  arguments: Record<string, unknown>;
  data: unknown;
  answer: string;
};
