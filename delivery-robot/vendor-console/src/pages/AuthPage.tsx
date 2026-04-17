import { useState } from "react";

interface AuthPageProps {
  onLogin: (username: string, password: string) => boolean;
}

export default function AuthPage({ onLogin }: AuthPageProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  function submit() {
    if (mode === "signup") {
      setMessage("Signup demo only. Use vendor / password123 to log in.");
      return;
    }
    const ok = onLogin(username, password);
    setMessage(ok ? "" : "Invalid credentials. Use vendor / password123.");
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-xl p-6 shadow-xl">
        <h1 className="font-mono text-2xl font-bold text-center">Campus Eats</h1>
        <p className="text-zinc-400 text-sm text-center mt-1">Vendor Console Access</p>

        <div className="mt-6 grid grid-cols-2 bg-zinc-800 rounded p-1">
          <button
            onClick={() => setMode("login")}
            className={`rounded py-2 text-sm font-semibold ${mode === "login" ? "bg-zinc-700 text-zinc-100" : "text-zinc-400"}`}
          >
            Login
          </button>
          <button
            onClick={() => setMode("signup")}
            className={`rounded py-2 text-sm font-semibold ${mode === "signup" ? "bg-zinc-700 text-zinc-100" : "text-zinc-400"}`}
          >
            Sign Up
          </button>
        </div>

        <div className="mt-5 space-y-3">
          <label className="block">
            <span className="text-xs text-zinc-400">Username</span>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-zinc-800 border border-zinc-700 rounded text-sm"
              placeholder="vendor"
            />
          </label>
          <label className="block">
            <span className="text-xs text-zinc-400">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 px-3 py-2 bg-zinc-800 border border-zinc-700 rounded text-sm"
              placeholder="password123"
            />
          </label>
          <button
            onClick={submit}
            className="w-full py-2 bg-orange-500 hover:bg-orange-400 text-black rounded font-semibold text-sm"
          >
            {mode === "login" ? "Log In" : "Create Account"}
          </button>
        </div>

        {message && <p className="mt-3 text-xs text-amber-300">{message}</p>}

        <p className="mt-5 text-xs text-zinc-500">
          Demo account: <span className="text-zinc-300">vendor</span> /{" "}
          <span className="text-zinc-300">password123</span>
        </p>
      </div>
    </div>
  );
}
