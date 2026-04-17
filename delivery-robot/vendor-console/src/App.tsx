import { useEffect, useMemo, useState } from "react";
import { DEFAULT_MENU_ITEMS, DEFAULT_VENDOR_SETTINGS } from "./data/defaults";
import { useOrders } from "./hooks/useOrders";
import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";
import MenuPage from "./pages/MenuPage";
import OrderHistoryPage from "./pages/OrderHistoryPage";
import SettingsPage from "./pages/SettingsPage";
import type { MenuItem, VendorSettings } from "./types";

type PageKey = "dashboard" | "history" | "menu" | "settings";

const SESSION_KEY = "vendor_console_session";
const SETTINGS_KEY = "vendor_console_settings";
/** v2: 15 items across 5 categories; bump key so old 3-item caches are replaced */
const MENU_KEY = "vendor_console_menu_v2";

function readJson<T>(key: string, fallback: T): T {
  const raw = localStorage.getItem(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

export default function App() {
  const [activePage, setActivePage] = useState<PageKey>("dashboard");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => localStorage.getItem(SESSION_KEY) === "1"
  );
  const [settings, setSettings] = useState<VendorSettings>(() =>
    readJson(SETTINGS_KEY, DEFAULT_VENDOR_SETTINGS)
  );
  const [menuItems, setMenuItems] = useState<MenuItem[]>(() => {
    const loaded = readJson<MenuItem[]>(MENU_KEY, DEFAULT_MENU_ITEMS);
    return loaded.length >= 15 ? loaded : DEFAULT_MENU_ITEMS;
  });

  const {
    allOrders,
    newOrders,
    acceptedOrders,
    preparingOrders,
    readyOrders,
    isPaused,
    newOrderIds,
    updateOrderStatus,
    togglePause,
  } = useOrders({ autoAcceptOrders: settings.autoAcceptOrders });

  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    localStorage.setItem(MENU_KEY, JSON.stringify(menuItems));
  }, [menuItems]);

  const shellClasses = useMemo(() => {
    if (settings.theme === "light") {
      return "h-screen bg-zinc-100 text-zinc-900";
    }
    return "h-screen bg-zinc-950 text-zinc-100";
  }, [settings.theme]);
  const isLight = settings.theme === "light";

  function login(username: string, password: string): boolean {
    const ok = username === "vendor" && password === "password123";
    if (ok) {
      localStorage.setItem(SESSION_KEY, "1");
      setIsAuthenticated(true);
    }
    return ok;
  }

  function logout() {
    localStorage.removeItem(SESSION_KEY);
    setIsAuthenticated(false);
    setActivePage("dashboard");
  }

  if (!isAuthenticated) {
    return <AuthPage onLogin={login} />;
  }

  return (
    <div className={`${shellClasses} flex flex-col font-sans`}>
      <header className={`grid grid-cols-3 items-center px-5 h-13 border-b shrink-0 relative ${isLight ? "border-zinc-300 bg-white text-zinc-900" : "border-zinc-800 bg-zinc-900 text-zinc-100"}`}>
        <button
          onClick={() => setIsMenuOpen(true)}
          className="flex items-center justify-start gap-2"
        >
          <span className="w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.7)]" />
          <span className="font-mono text-[18px] font-bold tracking-wide">Campus Eats</span>
        </button>
        <div className="flex items-center justify-center">
          <span className={`text-xs ${isLight ? "text-zinc-600" : "text-zinc-400"}`}>
            {settings.isStoreOpen ? "Store Open" : "Store Closed"}
          </span>
        </div>
        <div className="flex justify-end items-center gap-2">
          <button onClick={logout} className={`px-3 py-1.5 rounded border text-xs ${isLight ? "border-zinc-300 text-zinc-700 hover:bg-zinc-100" : "border-zinc-700 text-zinc-300 hover:bg-zinc-800"}`}>
            Logout
          </button>
        </div>
      </header>

      {isMenuOpen && (
        <>
          <button
            aria-label="Close navigation"
            onClick={() => setIsMenuOpen(false)}
            className="fixed inset-0 bg-black/40 z-20"
          />
          <aside
            className={`fixed left-0 top-0 h-full w-72 z-30 border-r p-4 ${isLight ? "bg-white border-zinc-300 text-zinc-900" : "bg-zinc-900 border-zinc-700 text-zinc-100"}`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-lg font-bold tracking-wide">Campus Eats</span>
              <button
                onClick={() => setIsMenuOpen(false)}
                className={`px-2 py-1 rounded text-sm ${isLight ? "hover:bg-zinc-100" : "hover:bg-zinc-800"}`}
              >
                ✕
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {[
                { key: "dashboard", label: "Dashboard" },
                { key: "history", label: "Order History" },
                { key: "menu", label: "Menu" },
                { key: "settings", label: "Settings" },
              ].map((item) => (
                <button
                  key={item.key}
                  onClick={() => {
                    setActivePage(item.key as PageKey);
                    setIsMenuOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded text-sm border ${
                    activePage === item.key
                      ? isLight
                        ? "bg-zinc-100 border-zinc-300"
                        : "bg-zinc-800 border-zinc-700"
                      : isLight
                        ? "border-zinc-200 hover:bg-zinc-100"
                        : "border-zinc-800 hover:bg-zinc-800"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </aside>
        </>
      )}

      <div className="flex-1 min-h-0">
        {activePage === "dashboard" && (
          <DashboardPage
            newOrders={newOrders}
            acceptedOrders={acceptedOrders}
            preparingOrders={preparingOrders}
            readyOrders={readyOrders}
            isPaused={isPaused}
            isLight={isLight}
            newOrderIds={newOrderIds}
            onTogglePause={togglePause}
            onUpdateStatus={updateOrderStatus}
          />
        )}
        {activePage === "history" && <OrderHistoryPage orders={allOrders} isLight={isLight} />}
        {activePage === "menu" && <MenuPage items={menuItems} isLight={isLight} onChange={setMenuItems} />}
        {activePage === "settings" && <SettingsPage value={settings} isLight={isLight} onChange={setSettings} />}
      </div>
    </div>
  );
}
