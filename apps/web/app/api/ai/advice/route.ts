import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    if (!body.query || body.query.length < 3 || body.query.length > 1000) {
      return NextResponse.json(
        { detail: "Query must be between 3 and 1000 characters." },
        { status: 400 }
      );
    }

    const res = await fetch(`${BACKEND_URL}/advice`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { detail: data.detail || "Backend service error" },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { detail: "Could not reach the server. Please try again later." },
      { status: 502 }
    );
  }
}