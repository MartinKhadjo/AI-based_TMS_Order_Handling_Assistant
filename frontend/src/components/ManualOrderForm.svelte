<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { PlusCircle } from 'lucide-svelte';
  import { api } from '../lib/api';
  import type { Customer, Vehicle } from '../lib/types';

  export let customers: Customer[] = [];
  export let vehicles: Vehicle[] = [];

  const dispatch = createEventDispatcher();
  let customer = '';
  let vehicle = '';
  let pickup_location = '';
  let delivery_location = '';
  let requested_pickup_date = '';
  let requested_delivery_date = '';
  let priority = 'normal';
  let error = '';
  let success = '';
  let saving = false;

  async function submit() {
    error = '';
    success = '';
    saving = true;
    try {
      await api.createOrder({
        customer: Number(customer),
        vehicle: Number(vehicle),
        pickup_location,
        delivery_location,
        requested_pickup_date: requested_pickup_date || null,
        requested_delivery_date: requested_delivery_date || null,
        priority
      });
      pickup_location = '';
      delivery_location = '';
      requested_pickup_date = '';
      requested_delivery_date = '';
      success = 'Order created.';
      dispatch('created');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Order creation failed';
    } finally {
      saving = false;
    }
  }
</script>

<section class="panel">
  <div class="panel-heading">
    <div>
      <p class="eyebrow">Manual Entry</p>
      <h2>New Order</h2>
    </div>
  </div>

  <form class="form-grid" on:submit|preventDefault={submit}>
    <label>
      Customer
      <select bind:value={customer} required>
        <option value="" disabled>Select customer</option>
        {#each customers as item}
          <option value={item.id}>{item.name}</option>
        {/each}
      </select>
    </label>
    <label>
      Vehicle
      <select bind:value={vehicle} required>
        <option value="" disabled>Select vehicle</option>
        {#each vehicles as item}
          <option value={item.id}>{item.brand} {item.model} · {item.vin}</option>
        {/each}
      </select>
    </label>
    <label>
      Pickup
      <input bind:value={pickup_location} required placeholder="Duesseldorf" />
    </label>
    <label>
      Delivery
      <input bind:value={delivery_location} required placeholder="Muenchen" />
    </label>
    <label>
      Pickup Date
      <input type="date" bind:value={requested_pickup_date} />
    </label>
    <label>
      Delivery Date
      <input type="date" bind:value={requested_delivery_date} />
    </label>
    <label>
      Priority
      <select bind:value={priority}>
        <option value="low">Low</option>
        <option value="normal">Normal</option>
        <option value="high">High</option>
        <option value="express">Express</option>
      </select>
    </label>
    <button class="primary-button" disabled={saving} title="Create order">
      <PlusCircle size={17} /> Create
    </button>
  </form>

  {#if error}
    <p class="notice error">{error}</p>
  {/if}
  {#if success}
    <p class="notice success">{success}</p>
  {/if}
</section>
