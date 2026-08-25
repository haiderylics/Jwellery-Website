/**
 * WhatsApp Order & Consultation Message Generator
 */

import { CartItemResolved, DeliverySettings } from "@/types/api";

export interface CustomerOrderInfo {
  fullName: string;
  phone: string;
  city: string;
  deliveryAddress: string;
  orderNotes?: string;
}

export function formatPricePKR(amount: number | string): string {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return "PKR 0";
  return `PKR ${num.toLocaleString("en-PK", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

const MAX_WHATSAPP_MESSAGE_LENGTH = 3500;

function sanitizeField(value?: string, maxLength = 300): string {
  if (!value) return "";
  return value
    .replace(/[\x00-\x1F\x7F]/g, "") // strip control chars
    .trim()
    .slice(0, maxLength);
}

export function buildWhatsAppOrderUrl(
  whatsappNumber: string,
  customer: CustomerOrderInfo,
  cartItems: CartItemResolved[],
  deliverySettings: DeliverySettings | null,
  siteUrl: string,
  brandName?: string
): string {
  // Normalize destination phone number (remove +, spaces, hyphens)
  const cleanPhone = whatsappNumber.replace(/[^0-9]/g, "") || "923001234567";
  const baseUrl = siteUrl.replace(/\/$/, "");
  const brand = (brandName || "Fine Jewels").toUpperCase();

  const subtotal = cartItems.reduce((sum, item) => sum + item.lineTotal, 0);
  const freeThreshold = deliverySettings ? parseFloat(deliverySettings.free_delivery_threshold) : 5000;
  const standardFee = deliverySettings ? parseFloat(deliverySettings.pakistan_delivery_charge) : 250;

  const isFreeDelivery = subtotal >= freeThreshold;
  const deliveryFee = isFreeDelivery ? 0 : standardFee;
  const grandTotal = subtotal + deliveryFee;

  const cleanName = sanitizeField(customer.fullName, 100);
  const cleanCustomerPhone = sanitizeField(customer.phone, 50);
  const cleanCity = sanitizeField(customer.city, 80);
  const cleanAddress = sanitizeField(customer.deliveryAddress, 250);
  const cleanNotes = sanitizeField(customer.orderNotes, 300);

  // Build structured message lines
  const lines: string[] = [
    `✨ *NEW ORDER INQUIRY — ${brand}* ✨`,
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "👤 *CUSTOMER DETAILS:*",
    `• *Name:* ${cleanName}`,
    `• *Phone:* ${cleanCustomerPhone}`,
    `• *City:* ${cleanCity}`,
    `• *Delivery Address:* ${cleanAddress}`,
  ];

  if (cleanNotes) {
    lines.push(`• *Notes / Custom Request:* ${cleanNotes}`);
  }

  lines.push("", "🛍️ *ORDER ITEMS:*");

  cartItems.forEach((item, index) => {
    const variantLabel = item.variant ? ` (${sanitizeField(item.variant.name, 50)})` : "";
    const productUrl = `${baseUrl}/product/${encodeURIComponent(item.product.slug)}`;
    lines.push(
      `${index + 1}. *${sanitizeField(item.product.name, 80)}*${variantLabel}`,
      `   Qty: ${item.quantity} × ${formatPricePKR(item.unitPrice)} = *${formatPricePKR(item.lineTotal)}*`,
      `   🔗 ${productUrl}`
    );
  });

  lines.push(
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    `💰 *Subtotal:* ${formatPricePKR(subtotal)}`,
    `🚚 *Shipping (Pakistan):* ${isFreeDelivery ? "FREE (Order over " + formatPricePKR(freeThreshold) + ")" : formatPricePKR(deliveryFee)}`,
    `💎 *ESTIMATED TOTAL:* *${formatPricePKR(grandTotal)}*`,
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "Please confirm item availability, customized sizing, and dispatch schedule. Thank you!"
  );

  let fullText = lines.join("\n");
  if (fullText.length > MAX_WHATSAPP_MESSAGE_LENGTH) {
    // Graceful compaction if cart size is abnormal
    fullText = fullText.slice(0, MAX_WHATSAPP_MESSAGE_LENGTH - 40) + "\n...[Items truncated for length]";
  }

  return `https://wa.me/${cleanPhone}?text=${encodeURIComponent(fullText)}`;
}

export function buildDirectConsultationUrl(
  whatsappNumber: string,
  productName: string,
  productSlug: string,
  siteUrl: string,
  brandName?: string
): string {
  const cleanPhone = whatsappNumber.replace(/[^0-9]/g, "") || "923001234567";
  const productUrl = `${siteUrl.replace(/\/$/, "")}/product/${encodeURIComponent(productSlug)}`;
  const cleanTitle = sanitizeField(productName, 80);
  const brand = brandName || "Jewels";
  const text = `Hello ${brand}, I am inquiring about *${cleanTitle}* (${productUrl}). Please share customization details and availability.`;
  return `https://wa.me/${cleanPhone}?text=${encodeURIComponent(text)}`;
}
