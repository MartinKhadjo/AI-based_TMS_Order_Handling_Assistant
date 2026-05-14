<!--
  Copyright (c) 2026 Martin Khadjavian. All rights reserved.
  Website: https://martinkhadjavian.com
-->

<script lang="ts">
  export let value: string;

  const labels: Record<string, string> = {
    open: 'Open',
    planned: 'Planned',
    in_transit: 'In transit',
    delivered: 'Delivered',
    cancelled: 'Cancelled',
    available: 'Available',
    assigned: 'Assigned',
    blocked: 'Blocked',
    express: 'Express',
    high: 'High',
    normal: 'Normal',
    low: 'Low'
  };

  $: label = labels[value] ?? value;
</script>

<span class={`status status-${value}`}>{label}</span>
