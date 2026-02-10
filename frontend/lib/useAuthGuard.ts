"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export function useAuthGuard() {
  const router = useRouter();

  useEffect(() => {

    const hasCookie = document.cookie
      .split("; ")
      .some((row) => row.startsWith("access="));


    const hasLocalToken = !!localStorage.getItem("access");

    if (!hasCookie && !hasLocalToken) {
      router.replace("/login");
    }
  }, [router]);
}
