<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  import { CarFront, MapPin } from 'lucide-svelte';
  import type { Vehicle } from '../lib/types';
  import StatusBadge from './StatusBadge.svelte';

  export let vehicles: Vehicle[] = [];
</script>

<section class="panel">
  <div class="panel-heading">
    <div>
      <p class="eyebrow">Fleet</p>
      <h2>Vehicles</h2>
    </div>
    <span class="count-pill">{vehicles.length}</span>
  </div>

  <div class="vehicle-grid">
    {#each vehicles as vehicle}
      <article class="vehicle-card">
        <div class="vehicle-icon"><CarFront size={22} /></div>
        <div>
          <h3>{vehicle.brand} {vehicle.model}</h3>
          <p>{vehicle.vin}</p>
          <div class="vehicle-footer">
            <StatusBadge value={vehicle.status} />
            <span><MapPin size={14} /> {vehicle.current_location || 'unknown'}</span>
          </div>
        </div>
      </article>
    {:else}
      <p class="empty-state">No vehicles yet.</p>
    {/each}
  </div>
</section>
