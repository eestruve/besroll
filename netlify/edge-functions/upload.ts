export default async (request: Request) => {
  // CORS Preflight
  if (request.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ success: false, error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }

  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!file) {
      return new Response(JSON.stringify({ success: false, error: "No file provided" }), {
        status: 400,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    // 1. Try Litterbox (Catbox) - 72h direct image hosting for Telegram/WhatsApp OpenGraph
    try {
      const litterData = new FormData();
      litterData.append("reqtype", "fileupload");
      litterData.append("time", "72h");
      litterData.append("fileToUpload", file);

      const upstreamRes = await fetch("https://litterbox.catbox.moe/resources/internals/api.php", {
        method: "POST",
        body: litterData,
      });

      const text = (await upstreamRes.text()).trim();
      if (text.startsWith("http://") || text.startsWith("https://")) {
        return new Response(JSON.stringify({ success: true, url: text }), {
          status: 200,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        });
      }
    } catch (_) {}

    // 2. Fallback to Uguu.se
    try {
      const uguuData = new FormData();
      uguuData.append("files[]", file);

      const uguuRes = await fetch("https://uguu.se/upload", {
        method: "POST",
        body: uguuData,
      });

      const uguuJson = await uguuRes.json();
      if (uguuJson && uguuJson.files && uguuJson.files.length > 0 && uguuJson.files[0].url) {
        return new Response(JSON.stringify({ success: true, url: uguuJson.files[0].url }), {
          status: 200,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        });
      }
    } catch (_) {}

    return new Response(JSON.stringify({ success: false, error: "All upload providers failed" }), {
      status: 502,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ success: false, error: String(err) }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }
};
