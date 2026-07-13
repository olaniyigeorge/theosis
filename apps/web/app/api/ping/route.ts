import { NextRequest } from "next/server";




export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  // TODO: ping your backend, e.g.:
  // const res = await fetch(`${process.env.API_BASE_URL}/health`);
  // return new Response(JSON.stringify({ ok: res.ok }), { status: 200 });

  return new Response('pong', { status: 200 });
}