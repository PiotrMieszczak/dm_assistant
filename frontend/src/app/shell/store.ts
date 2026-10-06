import { useEffect } from "react";
import { create } from "zustand";

const MOBILE_QUERY = "(max-width: 900px)";

function isMobileViewport() {
  return typeof window !== "undefined" && window.matchMedia(MOBILE_QUERY).matches;
}

type ShellStore = {
  mob: boolean;
  panelOpen: boolean;
  openPanel: () => void;
  closePanel: () => void;
  applyLayoutMode: (mob: boolean) => void;
};

export const useShellStore = create<ShellStore>((set) => {
  const mob = isMobileViewport();
  return {
    mob,
    panelOpen: !mob,
    openPanel: () => set({ panelOpen: true }),
    closePanel: () => set({ panelOpen: false }),
    applyLayoutMode: (nextMob) => set({ mob: nextMob, panelOpen: !nextMob }),
  };
});

/** Tracks the 900px behaviour switch. Crossing the breakpoint resets the
 *  panel to its default: open on desktop, closed on mobile. */
export function useLayoutMode() {
  const applyLayoutMode = useShellStore((state) => state.applyLayoutMode);

  useEffect(() => {
    const media = window.matchMedia(MOBILE_QUERY);
    const apply = () => applyLayoutMode(media.matches);
    apply();
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, [applyLayoutMode]);
}
