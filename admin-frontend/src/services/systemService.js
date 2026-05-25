const GATEWAY = import.meta.env.VITE_BFF_URL || 'http://localhost:8009';

const SERVICE_LABELS = {
  auth:            'Auth Service',
  inventory:       'Inventory Service',
  catalog:         'Catalog Service',
  pricing:         'Pricing Service',
  enrichment:        'AI Enrichment',
  quality:         'Data Quality',
  config:          'Config Module',
};

export async function getServicesHealth() {
  const bffEntry = { name: 'BFF Gateway', key: 'bff', status: 'offline' };

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 4000);
    const res = await fetch(`${GATEWAY}/health`, { signal: controller.signal });
    clearTimeout(timer);

    if (!res.ok) {
      return [{ ...bffEntry, status: 'degraded' }];
    }

    const data = await res.json();
    bffEntry.status = 'online';

    const serviceEntries = Object.entries(data.services ?? {})
      .filter(([key]) => key in SERVICE_LABELS)
      .map(([key, info]) => ({
        name: SERVICE_LABELS[key],
        key,
        status: info.status === 'ok' ? 'online' : 'degraded',
      }));

    return [bffEntry, ...serviceEntries];
  } catch {
    return [bffEntry];
  }
}
