<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  import { MessageSquareText, Play } from 'lucide-svelte';
  import { api } from '../lib/api';
  import type { ToolQueryResponse } from '../lib/types';

  let message = 'Welche Fahrzeuge sind noch nicht disponiert?';
  let result: ToolQueryResponse | null = null;
  let loading = false;
  let error = '';

  async function runQuery() {
    loading = true;
    error = '';
    try {
      result = await api.queryOrders(message);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Query failed';
    } finally {
      loading = false;
    }
  }
</script>

<section class="panel">
  <div class="panel-heading">
    <div>
      <p class="eyebrow">Tool Calling</p>
      <h2>Operational Query</h2>
    </div>
    <MessageSquareText size={20} />
  </div>

  <div class="query-row">
    <input bind:value={message} aria-label="Operational query" />
    <button class="primary-button" disabled={loading} on:click={runQuery} title="Run query">
      <Play size={17} /> Run
    </button>
  </div>

  {#if result}
    <div class="tool-result">
      <span class="tool-name">{result.tool}</span>
      <p>{result.answer}</p>
      <pre>{JSON.stringify(result.data, null, 2)}</pre>
    </div>
  {/if}

  {#if error}
    <p class="notice error">{error}</p>
  {/if}
</section>
