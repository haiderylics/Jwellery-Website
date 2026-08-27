import React, { useEffect, useState } from "react";
import {
  ArrowLeft,
  Check,
  MessageCircle,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Truck,
} from "lucide-react";
import { ProductDetail, ProductImage, ProductVariant, SiteSettings } from "@/types/api";
import { api } from "@/services/api";
import { cartActions } from "@/state/cartStore";
import { buildDirectConsultationUrl, formatPricePKR } from "@/utils/whatsapp";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ErrorState } from "@/components/ui/Feedback";
import { QuantityControl } from "@/components/ui/QuantityControl";
import { ResponsiveImage } from "@/components/ui/ResponsiveImage";
import { ProductVideoPlayer } from "@/components/ui/ProductVideoPlayer";

export interface ProductDetailPageProps {
  slug: string;
  settings: SiteSettings | null;
  onNavigate: (path: string) => void;
}

export const ProductDetailPage: React.FC<ProductDetailPageProps> = ({
  slug,
  settings,
  onNavigate,
}) => {
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [addedFeedback, setAddedFeedback] = useState(false);

  useEffect(() => {
    async function loadDetail() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProductDetail(slug);
        setProduct(data);
        if (data.variants && data.variants.length > 0) {
          setSelectedVariant(data.variants[0]);
        }
      } catch (err: any) {
        setError(err?.message || "Could not find requested jewellery piece.");
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [slug]);

  if (loading) {
    return (
      <div className="page-container detail-loading">
        <div className="detail-skeleton-grid">
          <div className="detail-gallery-skeleton skeleton" />
          <div className="detail-info-skeleton">
            <div className="skeleton-line skeleton w-1/3" />
            <div className="skeleton-line skeleton w-2/3 h-8 mt-2" />
            <div className="skeleton-line skeleton w-1/4 mt-4" />
            <div className="skeleton-line skeleton w-full h-24 mt-6" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="page-container">
        <ErrorState
          title="Product Not Found"
          message={error || "This piece may have been retired or moved."}
          actionLabel="Back to Shop"
          onAction={() => onNavigate("/shop")}
        />
      </div>
    );
  }

  const images: ProductImage[] = product.images || [];
  const activeImage = images[activeImageIndex] || null;

  const currentPrice = selectedVariant?.effective_price
    ? Number(selectedVariant.effective_price)
    : Number(product.base_price);

  const isOutOfStock =
    product.stock_status === "out_of_stock" ||
    (selectedVariant ? !selectedVariant.is_available : false);

  const handleAddToCart = () => {
    if (isOutOfStock) return;
    cartActions.addItem(product.slug, selectedVariant?.id || null, quantity);
    setAddedFeedback(true);
    setTimeout(() => setAddedFeedback(false), 2500);
  };

  const whatsappPhone = settings?.whatsapp_number || "";
  const canonicalUrl = settings?.canonical_site_url || "https://www.zirconiajewels.com";
  const whatsappInquiryUrl = buildDirectConsultationUrl(
    whatsappPhone,
    product.name,
    product.slug,
    canonicalUrl
  );

  return (
    <div className="page-container product-detail-page">
      {/* Back Button */}
      <nav className="breadcrumb-nav" aria-label="Breadcrumb">
        <button type="button" className="back-link" onClick={() => onNavigate("/shop")}>
          <ArrowLeft size={16} />
          <span>Back to Collection</span>
        </button>
      </nav>

      <div className="product-detail-layout">
        {/* Left Column: Gallery & Video */}
        <div className="product-gallery-col">
          <div className="main-image-viewport">
            <ResponsiveImage
              image={activeImage}
              alt={activeImage?.alt_text || product.name}
              aspectRatio="1/1"
              priority={true}
              sizes="(max-width: 860px) 100vw, 50vw"
              className="detail-main-img-wrap"
            />

            <div className="detail-badges">
              {product.is_new_arrival && <Badge variant="gold">NEW</Badge>}
              {product.is_featured && !product.is_new_arrival && <Badge variant="dark">FEATURED</Badge>}
              {product.is_custom_order && <Badge variant="outline">CUSTOM ORDER</Badge>}
            </div>
          </div>

          {/* Thumbnail Strip */}
          {images.length > 1 && (
            <div className="thumbnail-strip" role="tablist" aria-label="Product image gallery">
              {images.map((img, idx) => (
                <button
                  key={img.id}
                  type="button"
                  className={`thumbnail-btn ${idx === activeImageIndex ? "active" : ""}`}
                  onClick={() => setActiveImageIndex(idx)}
                  aria-label={`View image ${idx + 1}`}
                >
                  <ResponsiveImage
                    image={img}
                    alt={img.alt_text || ""}
                    aspectRatio="1/1"
                    sizes="72px"
                  />
                </button>
              ))}
            </div>
          )}

          {/* Video Demonstration Player */}
          {product.video?.video_url && (
            <div className="mt-6">
              <ProductVideoPlayer video={product.video} />
            </div>
          )}
        </div>

        {/* Right Column: Buying Information & Actions */}
        <div className="product-info-col">
          {product.category && (
            <button
              type="button"
              className="detail-category-link"
              onClick={() => onNavigate(`/shop?category=${product.category?.slug}`)}
            >
              {product.category.name}
            </button>
          )}

          <h1 className="detail-title">{product.name}</h1>

          {/* Price & Compare Price */}
          <div className="detail-pricing">
            <span className="detail-price">{formatPricePKR(currentPrice)}</span>
            {product.compare_at_price && (
              <span className="detail-compare-price">
                {formatPricePKR(product.compare_at_price)}
              </span>
            )}
            <span className="tax-inclusive-note">(Prices in PKR, inclusive of all taxes)</span>
          </div>

          {/* Availability Indicator */}
          <div className="availability-row">
            {isOutOfStock ? (
              <span className="stock-chip out-of-stock">● Currently Out of Stock</span>
            ) : product.stock_status === "low_stock" ? (
              <span className="stock-chip low-stock">● Limited Stock Remaining</span>
            ) : (
              <span className="stock-chip in-stock">● In Stock &amp; Ready to Ship</span>
            )}
          </div>

          {/* Variant Selector */}
          {product.variants && product.variants.length > 0 && (
            <div className="variant-selection-box">
              <label className="variant-label">
                Select Option / Size:
                <span className="selected-variant-name">
                  {selectedVariant ? selectedVariant.name : "Choose an option"}
                </span>
              </label>
              <div className="variant-options-grid">
                {product.variants.map((v) => {
                  const isSelected = selectedVariant?.id === v.id;
                  return (
                    <button
                      key={v.id}
                      type="button"
                      className={`variant-btn ${isSelected ? "selected" : ""} ${!v.is_available ? "disabled" : ""}`}
                      onClick={() => setSelectedVariant(v)}
                      disabled={!v.is_available}
                    >
                      <span>{v.name}</span>
                      {v.price_override && (
                        <span className="variant-price">{formatPricePKR(v.price_override)}</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Short Description */}
          {product.short_description && (
            <p className="detail-short-desc">{product.short_description}</p>
          )}

          {/* Purchase Actions */}
          <div className="purchase-actions-box">
            <div className="quantity-and-add">
              <QuantityControl
                quantity={quantity}
                onIncrease={() => setQuantity((q) => Math.min(q + 1, 10))}
                onDecrease={() => setQuantity((q) => Math.max(q - 1, 1))}
              />
              <Button
                variant="primary"
                size="lg"
                onClick={handleAddToCart}
                disabled={isOutOfStock}
                leftIcon={addedFeedback ? <Check size={18} /> : <ShoppingBag size={18} />}
                className="flex-1"
              >
                {addedFeedback ? "Added to Cart!" : isOutOfStock ? "Sold Out" : "Add to Cart"}
              </Button>
            </div>

            <Button
              variant="whatsapp"
              size="lg"
              onClick={() => window.open(whatsappInquiryUrl, "_blank")}
              leftIcon={<MessageCircle size={18} />}
              className="w-full mt-3"
            >
              Order / Inquire on WhatsApp
            </Button>
          </div>

          {/* Custom Order Banner */}
          {product.is_custom_order && (
            <div className="custom-order-banner">
              <Sparkles size={20} className="banner-icon" />
              <div>
                <h4>Bespoke Customization Available</h4>
                <p>
                  Need a custom finger size, gold carat adjustment, or engraving? We offer personalized bespoke tailoring via WhatsApp.
                </p>
              </div>
            </div>
          )}

          {/* Delivery & Authenticity Trust Points */}
          <div className="trust-bullets">
            <div className="trust-bullet">
              <Truck size={18} />
              <span>Free Delivery in Pakistan on orders over PKR 5,000</span>
            </div>
            <div className="trust-bullet">
              <ShieldCheck size={18} />
              <span>Authentic Hallmarked Gold &amp; Atelier Craftsmanship</span>
            </div>
          </div>

          {/* Detailed Narrative Description */}
          {product.description && (
            <div className="detail-description-section">
              <h3 className="section-subtitle">Craftsmanship &amp; Details</h3>
              <p className="description-text">{product.description}</p>
            </div>
          )}

          {/* Product Attributes & Taxonomy Table */}
          {product.attributes && product.attributes.length > 0 && (
            <div className="attributes-specs-section">
              <h3 className="section-subtitle">Specifications</h3>
              <table className="specs-table">
                <tbody>
                  {product.attributes.map((attr) => (
                    <tr key={attr.id}>
                      <th scope="row">{attr.attribute_type_name}</th>
                      <td>{attr.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
