import React from "react";
import { Minus, Plus } from "lucide-react";

export interface QuantityControlProps {
  quantity: number;
  onIncrease: () => void;
  onDecrease: () => void;
  min?: number;
  max?: number;
}

export const QuantityControl: React.FC<QuantityControlProps> = ({
  quantity,
  onIncrease,
  onDecrease,
  min = 1,
  max = 99,
}) => {
  return (
    <div className="quantity-control">
      <button
        type="button"
        className="qty-btn"
        onClick={onDecrease}
        disabled={quantity <= min}
        aria-label="Decrease quantity"
      >
        <Minus size={14} />
      </button>
      <span className="qty-value" aria-live="polite">
        {quantity}
      </span>
      <button
        type="button"
        className="qty-btn"
        onClick={onIncrease}
        disabled={quantity >= max}
        aria-label="Increase quantity"
      >
        <Plus size={14} />
      </button>
    </div>
  );
};
