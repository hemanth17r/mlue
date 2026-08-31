/**
 * Universal Agent Motion & Tactile Physics Tokens
 * Derived from Golden Design Standards (SSOT)
 */

export const springSnappy = {
  type: 'spring',
  stiffness: 420,
  damping: 30,
};

export const springJelly = {
  type: 'spring',
  stiffness: 350,
  damping: 22,
  mass: 0.8,
};

export const springModal = {
  type: 'spring',
  stiffness: 340,
  damping: 28,
  mass: 0.9,
};

export const springSheet = {
  type: 'spring',
  stiffness: 300,
  damping: 32,
  mass: 0.95,
};

export const tapScale = {
  button: {
    whileTap: { scale: 0.96 },
    transition: springSnappy,
  },
  icon: {
    whileTap: { scale: 0.88 },
    transition: springSnappy,
  },
  fab: {
    whileHover: { scale: 1.06 },
    whileTap: { scale: 0.92 },
    transition: springSnappy,
  },
  pill: {
    whileTap: { scale: 0.95 },
    transition: springSnappy,
  },
  card: {
    whileHover: { scale: 1.01 },
    whileTap: { scale: 0.98 },
    transition: springSnappy,
  },
};

export const backdropVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

export const modalVariants = {
  initial: { opacity: 0, scale: 0.95, y: 16 },
  animate: { opacity: 1, scale: 1, y: 0, transition: springModal },
  exit: { opacity: 0, scale: 0.96, y: 12, transition: { duration: 0.15 } },
};

export const dropdownVariants = {
  initial: { opacity: 0, scale: 0.96, y: -6 },
  animate: { opacity: 1, scale: 1, y: 0, transition: springSnappy },
  exit: { opacity: 0, scale: 0.96, y: -6, transition: { duration: 0.12 } },
};
