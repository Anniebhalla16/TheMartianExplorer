import { NextResponse } from "next/server"

// GET /api/missions?query=<encodedXQuery>&howmany=-1 (optional)
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get("query") ?? ""
  const howmany = searchParams.get("howmany") ?? "-1"

  // Forward to eXist-DB (server-side, so no CORS issues in the browser)
  const remoteURL = `http://localhost:8080/exist/rest/db/martian-explorer/missions.xml?_query=${query}&_howmany=${howmany}`

  const res = await fetch(remoteURL, {
    headers: { Accept: "application/xml" },
  })

  if (!res.ok) {
    return NextResponse.json({ message: `eXist-DB error: ${res.status} ${res.statusText}` }, { status: res.status })
  }

  const xml = await res.text()
  return new NextResponse(xml, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  })
}
