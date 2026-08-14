import React from "react";

export interface BadgeProps {
  variant?: "gold" | "dark" | "outline" | "success" | "warning" | "error";
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = "gold", children, className = "" }) => {
  return <span className={`badge badge-${variant} ${className}`}>{children}</span>;
};
