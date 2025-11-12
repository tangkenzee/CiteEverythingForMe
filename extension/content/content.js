// Send the current tab URL to the popup via chrome.storage
chrome.runtime.sendMessage({ action: "capture_url", url: window.location.href });
