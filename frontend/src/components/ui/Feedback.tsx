import React from "react";
import { AlertCircle, RefreshCw, Sparkles } from "lucide-react";
import { Button } from "./Button";

export const ProductCardSkeleton: React.FC = () => (
  <div className="product-card skeleton-card">
    <div className="skeleton-image skeleton" />
    <div className="skeleton-body">
      <div className="skeleton-line skeleton line-category" />
      <div className="skeleton-line skeleton line-title" />
      <div className="skeleton-line skeleton line-price" />
    </div>
  </div>
);

export const ProductGridSkeleton: React.FC<{ count?: number }> = ({ count = 8 }) => (
  <div className="product-grid">
    {Array.from({ length: count }).map((_, i) => (
      <ProductCardSkeleton key={i} />
    ))}
  </div>
);

export const EmptyState: React.FC<{
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({ title, description, actionLabel, onAction }) => (
  <div className="empty-state">
    <Sparkles className="empty-icon" size={36} />
    <h3 className="empty-title">{title}</h3>
    {description && <p className="empty-description">{description}</p>}
    {actionLabel && onAction && (
      <Button variant="outline" size="sm" onClick={onAction} className="mt-4">
        {actionLabel}
      </Button>
    )}
  </div>
);

export const ErrorState: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
  actionLabel?: string;
  onAction?: () => void;
}> = ({ title = "Something went wrong", message, onRetry, actionLabel, onAction }) => (
  <div className="error-state">
    <AlertCircle className="error-icon" size={36} />
    <h3 className="error-title">{title}</h3>
    <p className="error-message">{message}</p>
    {onRetry && (
      <Button
        variant="secondary"
        size="sm"
        onClick={onRetry}
        leftIcon={<RefreshCw size={14} />}
        className="mt-4"
      >
        Try Again
      </Button>
    )}
    {actionLabel && onAction && (
      <Button variant="outline" size="sm" onClick={onAction} className="mt-4">
        {actionLabel}
      </Button>
    )}
  </div>
);
