<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { CheckCircle2, Clock3, PackageCheck, Route, Truck } from 'lucide-svelte';
  import { api } from '../lib/api';
  import type { TransportOrder } from '../lib/types';
  import StatusBadge from './StatusBadge.svelte';

  export let orders: TransportOrder[] = [];

  const dispatch = createEventDispatcher();
  let busyOrderId: number | null = null;
  let error = '';

  async function setStatus(order: TransportOrder, status: string) {
    busyOrderId = order.id;
    error = '';
    try {
      await api.updateOrderStatus(order.id, status);
      dispatch('changed');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Status update failed';
    } finally {
      busyOrderId = null;
    }
  }
</script>

<section class="panel">
  <div class="panel-heading">
    <div>
      <p class="eyebrow">Transport Orders</p>
      <h2>Operational Queue</h2>
    </div>
    <span class="count-pill">{orders.length}</span>
  </div>

  {#if error}
    <p class="notice error">{error}</p>
  {/if}

  <div class="order-list">
    {#each orders as order}
      <article class="order-card">
        <div class="order-main">
          <div class="order-title">
            <span class="icon-bubble"><Route size={18} /></span>
            <div>
              <h3>#{order.id} {order.pickup_location} -> {order.delivery_location}</h3>
              <p>{order.customer_detail.name} · {order.vehicle_detail.brand} {order.vehicle_detail.model}</p>
            </div>
          </div>
          <div class="order-meta">
            <StatusBadge value={order.status} />
            <StatusBadge value={order.priority} />
            {#if order.created_by_ai}
              <span class="ai-chip">AI</span>
            {/if}
          </div>
        </div>

        <div class="order-details">
          <span>VIN {order.vehicle_detail.vin}</span>
          <span>Pickup {order.requested_pickup_date ?? 'not set'}</span>
          <span>Delivery {order.requested_delivery_date ?? 'not set'}</span>
        </div>

        <div class="order-actions">
          <button
            title="Set planned"
            class="ghost-button"
            disabled={busyOrderId === order.id}
            on:click={() => setStatus(order, 'planned')}
          >
            <Clock3 size={16} /> Planned
          </button>
          <button
            title="Set in transit"
            class="ghost-button"
            disabled={busyOrderId === order.id}
            on:click={() => setStatus(order, 'in_transit')}
          >
            <Truck size={16} /> Transit
          </button>
          <button
            title="Set delivered"
            class="ghost-button"
            disabled={busyOrderId === order.id}
            on:click={() => setStatus(order, 'delivered')}
          >
            <PackageCheck size={16} /> Delivered
          </button>
        </div>

        {#if order.tracking_events?.length}
          <div class="tracking-strip">
            <CheckCircle2 size={15} />
            <span>{order.tracking_events[0].event_type} · {order.tracking_events[0].location}</span>
          </div>
        {/if}
      </article>
    {:else}
      <p class="empty-state">No transport orders yet.</p>
    {/each}
  </div>
</section>
