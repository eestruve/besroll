export default async (request: Request) => {
  // Handle CORS preflight
  if (request.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  const url = new URL(request.url);
  const targetUrl = url.searchParams.get("url");

  if (!targetUrl) {
    return new Response(JSON.stringify({ error: "Missing 'url' parameter" }), {
      status: 400,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }

  try {
    // Validate URL
    const parsedUrl = new URL(targetUrl.startsWith("http") ? targetUrl : `https://${targetUrl}`);
    
    // Fetch target webpage with modern browser headers
    const response = await fetch(parsedUrl.toString(), {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
      },
      signal: AbortSignal.timeout(6000),
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const html = await response.text();

    // Helper regex to extract meta tags
    const getMeta = (property: string, nameFallback?: string): string => {
      // Check property="og:..." content="..."
      const propRegex = new RegExp(`<meta[^>]*property=["']${property}["'][^>]*content=["']([^"']+)["']`, "i");
      const propMatch = html.match(propRegex);
      if (propMatch && propMatch[1]) return decodeHtmlEntities(propMatch[1]);

      // Check content="..." property="og:..."
      const propRevRegex = new RegExp(`<meta[^>]*content=["']([^"']+)["'][^>]*property=["']${property}["']`, "i");
      const propRevMatch = html.match(propRevRegex);
      if (propRevMatch && propRevMatch[1]) return decodeHtmlEntities(propRevMatch[1]);

      if (nameFallback) {
        // Check name="..." content="..."
        const nameRegex = new RegExp(`<meta[^>]*name=["']${nameFallback}["'][^>]*content=["']([^"']+)["']`, "i");
        const nameMatch = html.match(nameRegex);
        if (nameMatch && nameMatch[1]) return decodeHtmlEntities(nameMatch[1]);

        const nameRevRegex = new RegExp(`<meta[^>]*content=["']([^"']+)["'][^>]*name=["']${nameFallback}["']`, "i");
        const nameRevMatch = html.match(nameRevRegex);
        if (nameRevMatch && nameRevMatch[1]) return decodeHtmlEntities(nameRevMatch[1]);
      }

      return "";
    };

    let title = getMeta("og:title", "twitter:title");
    if (!title) {
      const titleTagMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
      title = titleTagMatch ? decodeHtmlEntities(titleTagMatch[1].trim()) : "";
    }

    let description = getMeta("og:description", "description") || getMeta("twitter:description");
    let image = getMeta("og:image", "twitter:image");

    // Make relative image URLs absolute
    if (image && !image.startsWith("http")) {
      try {
        image = new URL(image, parsedUrl.origin).toString();
      } catch (_) {
        // Keep as-is if invalid
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        url: parsedUrl.toString(),
        title: title || parsedUrl.hostname,
        description: description || "Нажмите, чтобы прочитать подробности...",
        image: image || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800",
        domain: parsedUrl.hostname,
      }),
      {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  } catch (err: any) {
    return new Response(
      JSON.stringify({
        success: false,
        error: err.message || "Failed to scrape URL",
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  }
};

function decodeHtmlEntities(str: string): string {
  return str
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&#(\d+);/g, (_, dec) => String.fromCharCode(dec));
}
