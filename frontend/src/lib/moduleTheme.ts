export interface ModuleTheme {
  module: number;
  name: string;
  shortName: string;
  colorHex: string;
  badgeBg: string;
  badgeText: string;
  borderAccent: string;
  gradientFrom: string;
  glowColor: string;
}

export const MODULE_THEMES: Record<number, ModuleTheme> = {
  1: {
    module: 1,
    name: "Roots of Equations & Linear Systems",
    shortName: "Module I",
    colorHex: "#6d6af8",
    badgeBg: "bg-indigo-500/10",
    badgeText: "text-indigo-400",
    borderAccent: "border-indigo-500/30",
    gradientFrom: "from-indigo-500/20",
    glowColor: "rgba(109, 106, 248, 0.15)",
  },
  2: {
    module: 2,
    name: "Interpolation & Curve Fitting",
    shortName: "Module II",
    colorHex: "#2dd4bf",
    badgeBg: "bg-teal-500/10",
    badgeText: "text-teal-400",
    borderAccent: "border-teal-500/30",
    gradientFrom: "from-teal-500/20",
    glowColor: "rgba(45, 212, 191, 0.15)",
  },
  3: {
    module: 3,
    name: "Numerical Differentiation & Integration",
    shortName: "Module III",
    colorHex: "#fb923c",
    badgeBg: "bg-amber-500/10",
    badgeText: "text-amber-400",
    borderAccent: "border-amber-500/30",
    gradientFrom: "from-amber-500/20",
    glowColor: "rgba(251, 146, 60, 0.15)",
  },
  4: {
    module: 4,
    name: "Initial Value Problems for ODEs",
    shortName: "Module IV",
    colorHex: "#f472b6",
    badgeBg: "bg-rose-500/10",
    badgeText: "text-rose-400",
    borderAccent: "border-rose-500/30",
    gradientFrom: "from-rose-500/20",
    glowColor: "rgba(244, 114, 182, 0.15)",
  },
  5: {
    module: 5,
    name: "Boundary Value Problems & Matrix Inversion",
    shortName: "Module V",
    colorHex: "#34d399",
    badgeBg: "bg-emerald-500/10",
    badgeText: "text-emerald-400",
    borderAccent: "border-emerald-500/30",
    gradientFrom: "from-emerald-500/20",
    glowColor: "rgba(52, 211, 153, 0.15)",
  },
};

export function getModuleTheme(moduleNum: number): ModuleTheme {
  return (
    MODULE_THEMES[moduleNum] || {
      module: moduleNum,
      name: `Module ${moduleNum}`,
      shortName: `Mod ${moduleNum}`,
      colorHex: "#6d6af8",
      badgeBg: "bg-indigo-500/10",
      badgeText: "text-indigo-400",
      borderAccent: "border-indigo-500/30",
      gradientFrom: "from-indigo-500/20",
      glowColor: "rgba(109, 106, 248, 0.15)",
    }
  );
}
