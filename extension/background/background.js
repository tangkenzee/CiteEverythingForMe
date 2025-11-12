let urlList = [];

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "capture_url") {
    if (!urlList.includes(msg.url)) {
      urlList.push(msg.url);
    }
  } else if (msg.action === "get_urls") {
    sendResponse({ urls: urlList });
  } else if (msg.action === "clear_urls") {
    urlList = [];
  } else if (msg.action === "set_urls") {
    if (Array.isArray(msg.urls)) {
      urlList = msg.urls.filter((url) => typeof url === "string" && url.trim().length > 0);
    }
  }
});
