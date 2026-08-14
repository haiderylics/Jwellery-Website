/**
 * Client-Side Cart Store
 *
 * Security Invariant: Persists ONLY untrusted identifiers { productSlug, variantId, quantity }
 * to localStorage. Never trusts prices, stock, or totals from storage.
 */

import { useEffect, useState } from "react";
import { CartItemResolved, CartItemStored, ProductDetail, ProductListItem } from "@/types/api";

const CART_STORAGE_KEY = "zirconia_cart_v1";

type CartListener = () => void;
const listeners = new Set<CartListener>();

function emitChange(): void {
  listeners.forEach((listener) => listener());
}

const MAX_ITEM_QUANTITY = 99;
const MAX_CART_ITEMS = 50;

function sanitizeQuantity(q: any): number {
  if (typeof q !== "number" || isNaN(q) || !isFinite(q)) return 1;
  const floored = Math.floor(q);
  if (floored < 1) return 0;
  return Math.min(floored, MAX_ITEM_QUANTITY);
}

export function getStoredCart(): CartItemStored[] {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    
    const validItems: CartItemStored[] = [];
    for (const item of parsed) {
      if (
        typeof item?.productSlug === "string" &&
        item.productSlug.length > 0 &&
        item.productSlug.length <= 150 &&
        (item?.variantId === null || typeof item?.variantId === "number")
      ) {
        const qty = sanitizeQuantity(item?.quantity);
        if (qty > 0) {
          validItems.push({
            productSlug: item.productSlug,
            variantId: item.variantId || null,
            quantity: qty,
          });
        }
      }
      if (validItems.length >= MAX_CART_ITEMS) break;
    }
    return validItems;
  } catch {
    return [];
  }
}

function saveCart(items: CartItemStored[]): void {
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  } catch {
    // LocalStorage full or disabled
  }
  emitChange();
}

export const cartActions = {
  addItem: (productSlug: string, variantId: number | null = null, quantity = 1): void => {
    if (!productSlug || typeof productSlug !== "string" || productSlug.length > 150) return;
    const cleanQty = sanitizeQuantity(quantity);
    if (cleanQty <= 0) return;

    const current = getStoredCart();
    const existingIndex = current.findIndex(
      (item) => item.productSlug === productSlug && item.variantId === variantId
    );

    if (existingIndex > -1) {
      current[existingIndex].quantity = sanitizeQuantity(
        current[existingIndex].quantity + cleanQty
      );
    } else {
      if (current.length < MAX_CART_ITEMS) {
        current.push({ productSlug, variantId, quantity: cleanQty });
      }
    }
    saveCart(current);
  },

  updateQuantity: (productSlug: string, variantId: number | null, quantity: number): void => {
    const cleanQty = sanitizeQuantity(quantity);
    if (cleanQty <= 0) {
      cartActions.removeItem(productSlug, variantId);
      return;
    }
    const current = getStoredCart();
    const target = current.find(
      (item) => item.productSlug === productSlug && item.variantId === variantId
    );
    if (target) {
      target.quantity = cleanQty;
      saveCart(current);
    }
  },

  removeItem: (productSlug: string, variantId: number | null): void => {
    const current = getStoredCart();
    const updated = current.filter(
      (item) => !(item.productSlug === productSlug && item.variantId === variantId)
    );
    saveCart(updated);
  },

  clearCart: (): void => {
    saveCart([]);
  },

  getItemCount: (): number => {
    return getStoredCart().reduce((sum, item) => sum + item.quantity, 0);
  },

  resolveCartItems: (
    stored: CartItemStored[],
    productsBySlug: Map<string, ProductListItem | ProductDetail>
  ): CartItemResolved[] => {
    const resolved: CartItemResolved[] = [];

    for (const item of stored) {
      const product = productsBySlug.get(item.productSlug);
      if (!product) continue;

      let variant = null;
      let unitPrice = Number(product.base_price);

      if ("variants" in product && Array.isArray(product.variants) && item.variantId) {
        variant = product.variants.find((v) => v.id === item.variantId) || null;
        if (variant && variant.price_override) {
          unitPrice = Number(variant.price_override);
        }
      }

      resolved.push({
        product,
        variant,
        quantity: item.quantity,
        unitPrice,
        lineTotal: unitPrice * item.quantity,
      });
    }

    return resolved;
  },
};

export function useCart() {
  const [items, setItems] = useState<CartItemStored[]>(getStoredCart());
  const [itemCount, setItemCount] = useState<number>(cartActions.getItemCount());

  useEffect(() => {
    const handleUpdate = () => {
      const stored = getStoredCart();
      setItems(stored);
      setItemCount(cartActions.getItemCount());
    };

    listeners.add(handleUpdate);
    return () => {
      listeners.delete(handleUpdate);
    };
  }, []);

  return {
    items,
    itemCount,
    addItem: cartActions.addItem,
    updateQuantity: cartActions.updateQuantity,
    removeItem: cartActions.removeItem,
    clearCart: cartActions.clearCart,
  };
}
