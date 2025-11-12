let urlList = [];

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "add_url") {
    if (typeof msg.url === "string") {
      const trimmed = msg.url.trim();
      if (trimmed && !urlList.includes(trimmed)) {
        urlList.push(trimmed);
      }
    }
    sendResponse({ urls: urlList });
  } else if (msg.action === "get_urls") {
    sendResponse({ urls: urlList });
  } else if (msg.action === "clear_urls") {
    urlList = [];
  } else if (msg.action === "set_urls") {
    if (Array.isArray(msg.urls)) {
      urlList = msg.urls
        .filter((url) => typeof url === "string")
        .map((url) => url.trim())
        .filter(Boolean);
    }
  }
});
