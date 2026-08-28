export interface RequestCacheOptions {
  maxEntries?: number;
  ttlMs?: number;
  now?: () => number;
}

interface CacheEntry<T> {
  expiresAt: number;
  pending: boolean;
  promise: Promise<T>;
}

/** Small, bounded promise cache for anonymous GET requests in one SPA session. */
export class GetRequestCache {
  private readonly entries = new Map<string, CacheEntry<unknown>>();
  private readonly maxEntries: number;
  private readonly now: () => number;
  private readonly ttlMs: number;

  constructor({ maxEntries = 64, ttlMs = 30_000, now = Date.now }: RequestCacheOptions = {}) {
    this.maxEntries = Math.max(1, maxEntries);
    this.ttlMs = Math.max(1, ttlMs);
    this.now = now;
  }

  get<T>(key: string, loader: () => Promise<T>, ttlMs = this.ttlMs): Promise<T> {
    const existing = this.entries.get(key) as CacheEntry<T> | undefined;
    if (existing?.pending || (existing && existing.expiresAt > this.now())) {
      return existing.promise;
    }
    if (existing) this.entries.delete(key);

    this.pruneExpired();
    while (this.entries.size >= this.maxEntries) {
      const oldestKey = this.entries.keys().next().value as string | undefined;
      if (oldestKey === undefined) break;
      this.entries.delete(oldestKey);
    }

    const entry: CacheEntry<T> = {
      expiresAt: Number.POSITIVE_INFINITY,
      pending: true,
      promise: Promise.resolve().then(loader),
    };
    entry.promise = entry.promise.then(
      (value) => {
        entry.pending = false;
        entry.expiresAt = this.now() + Math.max(1, ttlMs);
        return value;
      },
      (error: unknown) => {
        if (this.entries.get(key) === entry) this.entries.delete(key);
        throw error;
      },
    );
    this.entries.set(key, entry as CacheEntry<unknown>);
    return entry.promise;
  }

  invalidate(key: string): void {
    this.entries.delete(key);
  }

  clear(): void {
    this.entries.clear();
  }

  get size(): number {
    return this.entries.size;
  }

  private pruneExpired(): void {
    const now = this.now();
    for (const [key, entry] of this.entries) {
      if (!entry.pending && entry.expiresAt <= now) this.entries.delete(key);
    }
  }
}
