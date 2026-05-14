<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Bot, CarFront, ClipboardList, Database, RefreshCw, Route } from 'lucide-svelte';
  import AIOrderAssistant from './components/AIOrderAssistant.svelte';
  import ManualOrderForm from './components/ManualOrderForm.svelte';
  import OperationalQuery from './components/OperationalQuery.svelte';
  import TransportOrderList from './components/TransportOrderList.svelte';
  import VehicleList from './components/VehicleList.svelte';
  import { api } from './lib/api';
  import type { Customer, Dashboard, TransportOrder, Vehicle } from './lib/types';

  let customers: Customer[] = [];
  let vehicles: Vehicle[] = [];
  let orders: TransportOrder[] = [];
  let dashboard: Dashboard | null = null;
  let loading = true;
  let error = '';

  async function refresh() {
    loading = true;
    error = '';
    try {
      [dashboard, customers, vehicles, orders] = await Promise.all([
        api.getDashboard(),
        api.listCustomers(),
        api.listVehicles(),
        api.listOrders()
      ]);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Backend not reachable';
    } finally {
      loading = false;
    }
  }

  onMount(refresh);
</script>

<main>
  <header class="app-header">
    <div>
      <p class="eyebrow">AI-native TMS Prototype</p>
      <h1>LogiSense Demo Lite</h1>
    </div>
    <button class="icon-button" on:click={refresh} title="Refresh data" disabled={loading}>
      <RefreshCw size={18} />
    </button>
  </header>

  {#if error}
    <div class="connection-banner">
      <Database size={18} />
      <span>{error}</span>
    </div>
  {/if}

  <section class="metric-grid" aria-label="Dashboard metrics">
    <div class="metric">
      <ClipboardList size={21} />
      <span>{dashboard?.orders ?? 0}</span>
      <p>Orders</p>
    </div>
    <div class="metric">
      <Route size={21} />
      <span>{dashboard?.open_orders ?? 0}</span>
      <p>Open</p>
    </div>
    <div class="metric">
      <CarFront size={21} />
      <span>{dashboard?.vehicles ?? 0}</span>
      <p>Vehicles</p>
    </div>
    <div class="metric">
      <Bot size={21} />
      <span>{dashboard?.ai_created_orders ?? 0}</span>
      <p>AI Created</p>
    </div>
  </section>

  <div class="workspace-grid">
    <div class="primary-column">
      <TransportOrderList {orders} on:changed={refresh} />
      <VehicleList {vehicles} />
    </div>
    <aside class="side-column">
      <AIOrderAssistant on:created={refresh} />
      <OperationalQuery />
      <ManualOrderForm {customers} {vehicles} on:created={refresh} />
    </aside>
  </div>
</main>
