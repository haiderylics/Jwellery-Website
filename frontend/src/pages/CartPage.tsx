import React, { useEffect, useState } from "react";
import {
  CheckCircle,
  MessageCircle,
  ShoppingBag,
  Trash2,
  Truck,
} from "lucide-react";
import {
  CartItemResolved,
  DeliverySettings,
  ProductDetail,
  ProductListItem,
  SiteSettings,
} from "@/types/api";
import { api } from "@/services/api";
import { cartActions, useCart } from "@/state/cartStore";
import {
  buildWhatsAppOrderUrl,
  CustomerOrderInfo,
  formatPricePKR,
} from "@/utils/whatsapp";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState } from "@/components/ui/Feedback";
import { QuantityControl } from "@/components/ui/QuantityControl";

export interface CartPageProps {
  settings: SiteSettings | null;
  deliverySettings: DeliverySettings | null;
  onNavigate: (path: string) => void;
}

export const CartPage: React.FC<CartPageProps> = ({
  settings,
  deliverySettings,
  onNavigate,
}) => {
  const { items, updateQuantity, removeItem, clearCart } = useCart();
  const [resolvedItems, setResolvedItems] = useState<CartItemResolved[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Customer Form State
  const [customer, setCustomer] = useState<CustomerOrderInfo>({
    fullName: "",
    phone: "",
    city: "",
    deliveryAddress: "",
    orderNotes: "",
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [orderSent, setOrderSent] = useState(false);

  // Fetch authoritative product data for all cart slugs
  useEffect(() => {
    async function loadCartData() {
      if (items.length === 0) {
        setResolvedItems([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const uniqueSlugs = Array.from(new Set(items.map((i) => i.productSlug)));
        const productsMap = new Map<string, ProductListItem | ProductDetail>();

        // Fetch each unique product detail concurrently
        const fetchPromises = uniqueSlugs.map(async (slug) => {
          try {
            const prod = await api.getProductDetail(slug);
            productsMap.set(slug, prod);
          } catch {
            // Product might have been unpublished; skip
          }
        });

        await Promise.all(fetchPromises);
        const resolved = cartActions.resolveCartItems(items, productsMap);
        setResolvedItems(resolved);
      } catch (err: any) {
        setError(err?.message || "Failed to resolve live product pricing.");
      } finally {
        setLoading(false);
      }
    }

    loadCartData();
  }, [items]);

  if (loading) {
    return (
      <div className="page-container cart-loading">
        <h1 className="page-title">Your Shopping Bag</h1>
        <div className="skeleton-line skeleton h-32 mt-4" />
        <div className="skeleton-line skeleton h-32 mt-4" />
      </div>
    );
  }

  if (orderSent) {
    return (
      <div className="page-container order-success-page">
        <div className="success-card">
          <CheckCircle size={56} className="success-icon" />
          <h1 className="success-title">Order Request Transmitted</h1>
          <p className="success-desc">
            Your order details have been formatted and directed to our WhatsApp Concierge.
            Our master jewellery consultant will confirm your sizing, customization preferences, and delivery timeline immediately.
          </p>
          <div className="mt-6">
            <Button variant="primary" size="md" onClick={() => onNavigate("/shop")}>
              Continue Exploring Collection
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (resolvedItems.length === 0) {
    return (
      <div className="page-container">
        <h1 className="page-title">Your Shopping Bag</h1>
        <EmptyState
          title="Your shopping bag is empty"
          description="Explore our handcrafted gold and diamond collections to select your desired pieces."
          actionLabel="Discover Jewellery"
          onAction={() => onNavigate("/shop")}
        />
      </div>
    );
  }

  // Calculate Subtotal & Shipping
  const subtotal = resolvedItems.reduce((sum, item) => sum + item.lineTotal, 0);
  const freeThreshold = deliverySettings ? Number(deliverySettings.free_delivery_threshold) : 5000;
  const standardFee = deliverySettings ? Number(deliverySettings.pakistan_delivery_charge) : 250;
  const isFreeShipping = subtotal >= freeThreshold;
  const shippingFee = isFreeShipping ? 0 : standardFee;
  const grandTotal = subtotal + shippingFee;

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!customer.fullName.trim()) errors.fullName = "Please enter your full name.";
    if (!customer.phone.trim()) errors.phone = "Please provide your active WhatsApp / contact number.";
    if (!customer.city.trim()) errors.city = "Please enter your delivery city (e.g. Lahore, Karachi).";
    if (!customer.deliveryAddress.trim()) errors.deliveryAddress = "Please provide your street / house address.";

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleProceedToWhatsApp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    const whatsappNumber = settings?.whatsapp_number || "";
    const siteUrl = settings?.canonical_site_url || window.location.origin;

    const whatsappUrl = buildWhatsAppOrderUrl(
      whatsappNumber,
      customer,
      resolvedItems,
      deliverySettings,
      siteUrl
    );

    // Open WhatsApp
    window.open(whatsappUrl, "_blank", "noopener,noreferrer");

    // Clear cart and show confirmation
    clearCart();
    setOrderSent(true);
  };

  return (
    <div className="page-container cart-page">
      <div className="cart-header">
        <span className="section-kicker">REVIEW &amp; CHECKOUT</span>
        <h1 className="cart-title">Your Shopping Bag</h1>
      </div>

      {error && <ErrorState message={error} />}

      <div className="cart-layout">
        {/* Left Column: Line Items */}
        <div className="cart-items-col">
          <div className="cart-items-list">
            {resolvedItems.map((item) => {
              const primaryImg =
                "images" in item.product && item.product.images?.length > 0
                  ? item.product.images[0].image_url
                  : "primary_image" in item.product
                    ? item.product.primary_image?.image_url
                    : null;

              return (
                <div key={`${item.product.slug}-${item.variant?.id || "base"}`} className="cart-item-row">
                  <div className="cart-item-thumb">
                    {primaryImg ? (
                      <img src={primaryImg} alt={item.product.name} />
                    ) : (
                      <div className="thumb-placeholder">
                        <ShoppingBag size={20} />
                      </div>
                    )}
                  </div>

                  <div className="cart-item-info">
                    <h3
                      className="cart-item-title"
                      onClick={() => onNavigate(`/product/${item.product.slug}`)}
                    >
                      {item.product.name}
                    </h3>
                    {item.variant && (
                      <span className="cart-item-variant">Option: {item.variant.name}</span>
                    )}
                    <span className="cart-item-unit-price">
                      Unit: {formatPricePKR(item.unitPrice)}
                    </span>
                  </div>

                  <div className="cart-item-qty">
                    <QuantityControl
                      quantity={item.quantity}
                      onIncrease={() =>
                        updateQuantity(item.product.slug, item.variant?.id || null, item.quantity + 1)
                      }
                      onDecrease={() =>
                        updateQuantity(item.product.slug, item.variant?.id || null, item.quantity - 1)
                      }
                    />
                  </div>

                  <div className="cart-item-total">
                    <span className="line-total-price">{formatPricePKR(item.lineTotal)}</span>
                    <button
                      type="button"
                      className="remove-item-btn"
                      onClick={() => removeItem(item.product.slug, item.variant?.id || null)}
                      aria-label={`Remove ${item.product.name} from bag`}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="cart-footer-actions">
            <Button variant="ghost" size="sm" onClick={() => onNavigate("/shop")}>
              &larr; Add More Jewellery Pieces
            </Button>
            <button type="button" className="clear-cart-link" onClick={clearCart}>
              Empty Shopping Bag
            </button>
          </div>
        </div>

        {/* Right Column: Order Summary & Customer Delivery Form */}
        <div className="cart-summary-col">
          <div className="order-summary-box">
            <h3 className="summary-title">Order Summary</h3>

            <div className="summary-row">
              <span>Subtotal ({resolvedItems.length} items)</span>
              <span>{formatPricePKR(subtotal)}</span>
            </div>

            <div className="summary-row">
              <span className="shipping-label">
                <Truck size={16} />
                <span>Standard Delivery (Pakistan)</span>
              </span>
              <span>{isFreeShipping ? "FREE" : formatPricePKR(shippingFee)}</span>
            </div>

            {!isFreeShipping && (
              <div className="free-shipping-progress">
                <span>Add {formatPricePKR(freeThreshold - subtotal)} more for Free Shipping!</span>
              </div>
            )}

            <div className="summary-divider" />

            <div className="summary-row grand-total-row">
              <span>Estimated Total</span>
              <span className="grand-total-amount">{formatPricePKR(grandTotal)}</span>
            </div>

            {/* Customer Delivery Form */}
            <form className="customer-checkout-form" onSubmit={handleProceedToWhatsApp}>
              <h4 className="form-heading">Delivery &amp; Customer Details</h4>

              <div className="form-field">
                <label htmlFor="fullName">Full Name *</label>
                <input
                  id="fullName"
                  type="text"
                  placeholder="e.g. Fatima Ali"
                  value={customer.fullName}
                  onChange={(e) => setCustomer({ ...customer, fullName: e.target.value })}
                  className={formErrors.fullName ? "input-error" : ""}
                />
                {formErrors.fullName && <span className="field-error">{formErrors.fullName}</span>}
              </div>

              <div className="form-field">
                <label htmlFor="phone">WhatsApp / Mobile Number *</label>
                <input
                  id="phone"
                  type="tel"
                  placeholder="e.g. 0300 1234567"
                  value={customer.phone}
                  onChange={(e) => setCustomer({ ...customer, phone: e.target.value })}
                  className={formErrors.phone ? "input-error" : ""}
                />
                {formErrors.phone && <span className="field-error">{formErrors.phone}</span>}
              </div>

              <div className="form-field">
                <label htmlFor="city">City *</label>
                <input
                  id="city"
                  type="text"
                  placeholder="e.g. Lahore, Karachi, Islamabad"
                  value={customer.city}
                  onChange={(e) => setCustomer({ ...customer, city: e.target.value })}
                  className={formErrors.city ? "input-error" : ""}
                />
                {formErrors.city && <span className="field-error">{formErrors.city}</span>}
              </div>

              <div className="form-field">
                <label htmlFor="deliveryAddress">Complete Delivery Address *</label>
                <textarea
                  id="deliveryAddress"
                  rows={2}
                  placeholder="House / Apartment #, Street, Area"
                  value={customer.deliveryAddress}
                  onChange={(e) => setCustomer({ ...customer, deliveryAddress: e.target.value })}
                  className={formErrors.deliveryAddress ? "input-error" : ""}
                />
                {formErrors.deliveryAddress && (
                  <span className="field-error">{formErrors.deliveryAddress}</span>
                )}
              </div>

              <div className="form-field">
                <label htmlFor="orderNotes">Special Instructions / Ring Size (Optional)</label>
                <input
                  id="orderNotes"
                  type="text"
                  placeholder="e.g. Ring size 14, gift packaging"
                  value={customer.orderNotes}
                  onChange={(e) => setCustomer({ ...customer, orderNotes: e.target.value })}
                />
              </div>

              <Button
                type="submit"
                variant="whatsapp"
                size="lg"
                leftIcon={<MessageCircle size={20} />}
                className="w-full mt-4"
              >
                Send Order via WhatsApp
              </Button>

              <p className="checkout-note">
                🔒 Clicking will format your order details and open a direct chat with our verified WhatsApp Concierge. No payment is charged online.
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
