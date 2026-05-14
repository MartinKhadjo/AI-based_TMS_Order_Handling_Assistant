/*
 * Copyright (c) 2026 Martin Khadjavian. All rights reserved.
 * Website: https://martinkhadjavian.com
 */

import type {
  Customer,
  Dashboard,
  DraftOrder,
  ExtractionResponse,
  ToolQueryResponse,
  TransportOrder,
  Vehicle
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      message = body.detail ?? JSON.stringify(body);
    } catch {
      // Keep the HTTP status message.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getDashboard: () => request<Dashboard>('/dashboard/'),
  listCustomers: () => request<Customer[]>('/customers/'),
  listVehicles: () => request<Vehicle[]>('/vehicles/'),
  listOrders: () => request<TransportOrder[]>('/orders/'),
  createCustomer: (payload: Partial<Customer>) =>
    request<Customer>('/customers/', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  createVehicle: (payload: Partial<Vehicle>) =>
    request<Vehicle>('/vehicles/', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  createOrder: (payload: Record<string, unknown>) =>
    request<TransportOrder>('/orders/', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  updateOrderStatus: (id: number, status: string) =>
    request<TransportOrder>(`/orders/${id}/status/`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    }),
  extractOrder: (message: string) =>
    request<ExtractionResponse>('/ai/extract-order/', {
      method: 'POST',
      body: JSON.stringify({ message })
    }),
  createOrderDraft: (draft: DraftOrder, rawInput: string, confidence: number) =>
    request<TransportOrder>('/ai/create-order-draft/', {
      method: 'POST',
      body: JSON.stringify({ draft, raw_input: rawInput, confidence })
    }),
  queryOrders: (message: string) =>
    request<ToolQueryResponse>('/ai/query-orders/', {
      method: 'POST',
      body: JSON.stringify({ message })
    })
};
