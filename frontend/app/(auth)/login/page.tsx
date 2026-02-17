"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError(null);
    setLoading(true);

    try {
     
      const loginRes = await fetch("http://127.0.0.1:8000/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!loginRes.ok) {
        setError("Invalid email or password");
        return;
      }

      const loginData = await loginRes.json();

      const tokenRes = await fetch("http://127.0.0.1:8000/api/token/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!tokenRes.ok) {
        setError("Token generation failed");
        return;
      }

      const tokenData = await tokenRes.json();

    
      localStorage.setItem("access", tokenData.access);
      localStorage.setItem("refresh", tokenData.refresh);

      document.cookie = `access=${tokenData.access}; path=/;`;
      document.cookie = `refresh=${tokenData.refresh}; path=/;`;

     
      localStorage.setItem(
        "user",
        JSON.stringify({
          id: loginData.id,
          email: loginData.email,
          role: loginData.Role,
        })
      );
      localStorage.setItem("role", loginData.Role);

      
      router.replace("/dashboard");
    } catch (err) {
      console.error(err);
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-96 border p-6 rounded space-y-4">
        <h1 className="text-2xl font-bold text-center">Login</h1>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <input
          className="input"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="input"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          className="btn w-full"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
              <button
            className="text-sm text-blue-600 hover:underline"
            onClick={() =>
              router.push(
                "/register"
              )
            }
          >
            Login  Page Updated →
          </button>
      </div>
    </div>
  );
}
