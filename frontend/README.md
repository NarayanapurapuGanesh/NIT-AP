# FacultyIQ Frontend Architecture

The frontend is an enterprise web application constructed with **Next.js 15 (App Router)**, **TypeScript**, **Tailwind CSS**, **shadcn/ui**, and **Framer Motion**.

## 📁 Architecture Responsibilities

```
frontend/
├── app/                      # App Router structure
│   ├── (landing)/            # Landing page layout & routes
│   ├── (auth)/               # Authentication pages & layout
│   ├── (dashboard)/          # Application dashboard layout & sub-routes
│   ├── api/                  # BFF (Backend-for-Frontend) route handlers
│   ├── not-found.tsx         # Custom 404 page
│   ├── loading.tsx           # Suspense loading component
│   └── error.tsx             # Global error boundary
├── components/               # Reusable Component Library
│   ├── ui/                   # Design system components (Button, Card, Input, Modal, Loader)
│   ├── layout/               # Layout components (Header, Sidebar, Navigation)
│   └── feedback/             # Empty states, error states, spinners
├── config/                   # Site config & environment validation
├── lib/                      # Base API client & utility functions
└── styles/                   # Global CSS & Tailwind design tokens
```

## 🎨 Design System Principles

1. **Enterprise Aesthetics**: Sleek dark/light themes, subtle glassmorphism, and responsive modern typography.
2. **Component Isolation**: Zero ad-hoc inline styling; components use structured Tailwind design tokens.
3. **Accessibility & Motion**: Accessible UI primitives enhanced with silky Framer Motion animations.
