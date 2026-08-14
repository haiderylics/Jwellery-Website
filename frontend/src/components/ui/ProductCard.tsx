import React from "react";
import { ShoppingBag } from "lucide-react";
import { ProductListItem } from "@/types/api";
import { cartActions } from "@/state/cartStore";
import { formatPricePKR } from "@/utils/whatsapp";
import { Badge } from "./Badge";
import { ResponsiveImage } from "./ResponsiveImage";

export interface ProductCardProps {
  product: ProductListItem;
  onNavigate: (path: string) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onNavigate }) => {
  const isOutOfStock = product.stock_status === "out_of_stock";

  const handleQuickAdd = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isOutOfStock) {
      cartActions.addItem(product.slug, null, 1);
    }
  };

  const handleCardClick = () => {
    onNavigate(`/product/${product.slug}`);
  };

  return (
    <article className="product-card" onClick={handleCardClick} role="button" tabIndex={0}>
      <div className="product-image-container">
        <ResponsiveImage
          image={product.primary_image}
          alt={product.primary_image?.alt_text || product.name}
          aspectRatio="1/1"
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
          className="product-card-img-wrap"
        />

        <div className="product-badges">
          {product.is_new_arrival && <Badge variant="gold">NEW</Badge>}
          {product.is_featured && !product.is_new_arrival && <Badge variant="dark">FEATURED</Badge>}
          {product.is_custom_order && <Badge variant="outline">CUSTOM</Badge>}
          {isOutOfStock && <Badge variant="error">SOLD OUT</Badge>}
          {product.stock_status === "low_stock" && !isOutOfStock && (
            <Badge variant="warning">FEW LEFT</Badge>
          )}
        </div>

        {!isOutOfStock && (
          <button
            type="button"
            className="quick-add-btn"
            onClick={handleQuickAdd}
            aria-label={`Add ${product.name} to cart`}
          >
            <ShoppingBag size={16} />
            <span>Add to Cart</span>
          </button>
        )}
      </div>

      <div className="product-meta">
        {product.category && (
          <span className="product-category">{product.category.name}</span>
        )}
        <h3 className="product-name">{product.name}</h3>
        <div className="product-pricing">
          <span className="product-price">{formatPricePKR(product.base_price)}</span>
          {product.compare_at_price && (
            <span className="product-compare-price">
              {formatPricePKR(product.compare_at_price)}
            </span>
          )}
        </div>
      </div>
    </article>
  );
};
