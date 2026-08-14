import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "whatsapp" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  className = "",
  disabled,
  ...props
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="btn-spinner" aria-hidden="true" />
      ) : (
        <>
          {leftIcon && <span className="btn-icon left">{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span className="btn-icon right">{rightIcon}</span>}
        </>
      )}
    </button>
  );
};
