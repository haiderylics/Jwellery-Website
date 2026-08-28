import assert from "node:assert/strict";
import test from "node:test";

import { GetRequestCache } from "../src/services/requestCache.ts";

test("deduplicates concurrent requests and retains a successful value until TTL", async () => {
  let calls = 0;
  let now = 0;
  const cache = new GetRequestCache({ ttlMs: 50, now: () => now });
  const loader = async () => {
    calls += 1;
    return "value";
  };

  const [first, second] = await Promise.all([cache.get("/site", loader), cache.get("/site", loader)]);
  assert.equal(first, "value");
  assert.equal(second, "value");
  assert.equal(calls, 1);

  await cache.get("/site", loader);
  assert.equal(calls, 1);
  now = 51;
  await cache.get("/site", loader);
  assert.equal(calls, 2);
});

test("does not retain failed requests", async () => {
  let calls = 0;
  const cache = new GetRequestCache();
  const loader = async () => {
    calls += 1;
    throw new DOMException("cancelled", "AbortError");
  };

  await assert.rejects(cache.get("/product/ring", loader), { name: "AbortError" });
  await assert.rejects(cache.get("/product/ring", loader), { name: "AbortError" });
  assert.equal(calls, 2);
  assert.equal(cache.size, 0);
});

test("enforces the entry bound and supports explicit invalidation", async () => {
  const cache = new GetRequestCache({ maxEntries: 2 });
  await cache.get("one", async () => 1);
  await cache.get("two", async () => 2);
  await cache.get("three", async () => 3);
  assert.equal(cache.size, 2);
  cache.invalidate("three");
  assert.equal(cache.size, 1);
  cache.clear();
  assert.equal(cache.size, 0);
});
