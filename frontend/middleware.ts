import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PATHS = ["/dashboard", "/notes"];

export function middleware(req: NextRequest) {
  const accessToken = req.cookies.get("access")?.value;
  const pathname = req.nextUrl.pathname;

  const isProtected = PROTECTED_PATHS.some((path) =>
    pathname.startsWith(path)
  );


  if (isProtected && !accessToken) {
    const loginUrl = new URL("/login", req.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/notes/:path*"],
};
