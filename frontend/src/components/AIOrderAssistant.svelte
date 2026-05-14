<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Bot, Check, FileJson2, Sparkles } from 'lucide-svelte';
  import { api } from '../lib/api';
  import type { DraftOrder, ExtractionResponse } from '../lib/types';

  const dispatch = createEventDispatcher();
  const sample =
    'Bitte transportieren Sie einen BMW i4 mit VIN WBA123456789ABCDE von Duesseldorf nach Muenchen. Abholung am 12.06.2026, Lieferung bis 14.06.2026. Kunde ist Autohaus Mueller.';

  let message = sample;
  let result: ExtractionResponse | null = null;
  let draft: DraftOrder | null = null;
  let loading = false;
  let saving = false;
  let error = '';
  let success = '';

  async function extract() {
    loading = true;
    error = '';
    success = '';
    try {
      result = await api.extractOrder(message);
      draft = { ...result.draft };
    } catch (err) {
      error = err instanceof Error ? err.message : 'Extraction failed';
    } finally {
      loading = false;
    }
  }

  async function createOrder() {
    if (!draft || !result) return;
    saving = true;
    error = '';
    success = '';
    try {
      const order = await api.createOrderDraft(draft, message, result.confidence);
      success = `Order #${order.id} created.`;
      dispatch('created');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Draft creation failed';
    } finally {
      saving = false;
    }
  }
</script>

<section class="panel ai-panel">
  <div class="panel-heading">
    <div>
      <p class="eyebrow">AI Workflow</p>
      <h2>Order Assistant</h2>
    </div>
    <span class="icon-pill"><Bot size={18} /> Mock AI</span>
  </div>

  <textarea bind:value={message} rows="6" aria-label="Customer request"></textarea>
  <div class="button-row">
    <button class="primary-button" disabled={loading} on:click={extract} title="Extract transport data">
      <Sparkles size={17} /> Extract
    </button>
  </div>

  {#if result && draft}
    <div class="draft-layout">
      <div class="draft-form">
        <label>
          Customer
          <input bind:value={draft.customer_name} />
        </label>
        <label>
          Brand
          <input bind:value={draft.vehicle_brand} />
        </label>
        <label>
          Model
          <input bind:value={draft.vehicle_model} />
        </label>
        <label>
          VIN
          <input bind:value={draft.vin} />
        </label>
        <label>
          Pickup
          <input bind:value={draft.pickup_location} />
        </label>
        <label>
          Delivery
          <input bind:value={draft.delivery_location} />
        </label>
        <label>
          Pickup Date
          <input type="date" bind:value={draft.requested_pickup_date} />
        </label>
        <label>
          Delivery Date
          <input type="date" bind:value={draft.requested_delivery_date} />
        </label>
      </div>

      <div class="json-preview">
        <div class="json-header">
          <FileJson2 size={17} />
          <span>Confidence {Math.round(result.confidence * 100)}%</span>
        </div>
        <pre>{JSON.stringify(draft, null, 2)}</pre>
      </div>
    </div>

    {#if result.missing_fields.length || result.validation_errors.length || result.warnings.length}
      <div class="validation-list">
        {#each result.missing_fields as item}
          <span class="validation-chip error">Missing {item}</span>
        {/each}
        {#each result.validation_errors as item}
          <span class="validation-chip error">{item}</span>
        {/each}
        {#each result.warnings as item}
          <span class="validation-chip warning">{item}</span>
        {/each}
      </div>
    {/if}

    <button class="primary-button" disabled={saving} on:click={createOrder} title="Create order from draft">
      <Check size={17} /> Confirm Draft
    </button>
  {/if}

  {#if error}
    <p class="notice error">{error}</p>
  {/if}
  {#if success}
    <p class="notice success">{success}</p>
  {/if}
</section>
