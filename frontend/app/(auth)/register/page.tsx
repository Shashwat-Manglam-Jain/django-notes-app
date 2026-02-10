"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("user");

  async function handleRegister() {
    await fetch("http://127.0.0.1:8000/register/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, Role: role }),
    });

    window.location.href = "/login";
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-96 space-y-4">
        <h1 className="text-2xl font-bold">Register</h1>

        <input className="input" placeholder="Email" onChange={e => setEmail(e.target.value)} />
        <input className="input" type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />

        <select className="input" value={role} onChange={e => setRole(e.target.value)}>
          <option value="user">User</option>
          <option value="manager">Manager</option>
        </select>

        <button className="btn" onClick={handleRegister}>
          Register
        </button>
          <button
            className="text-sm text-blue-600 hover:underline"
            onClick={() =>
              router.push(
                "/login"
              )
            }
          >
            Login →
          </button>
      </div>
    </div>
  );
}
