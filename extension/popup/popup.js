const urlListEl = document.getElementById("url-list");
const styleEl = document.getElementById("style");
const useAiEl = document.getElementById("use-ai");
const addBtn = document.getElementById("add-btn");
const generateBtn = document.getElementById("generate-btn");
const clearBtn = document.getElementById("clear-btn");

function syncFromBackground() {
  chrome.runtime.sendMessage({ action: "get_urls" }, (response) => {
    urlListEl.value = (response?.urls || []).join("\n");
  });
}

syncFromBackground();

addBtn.addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const url = tabs[0]?.url;
    if (!url) {
      alert("No active tab URL found.");
      return;
    }

    chrome.runtime.sendMessage({ action: "add_url", url }, (response) => {
      urlListEl.value = (response?.urls || []).join("\n");
    });
  });
});

clearBtn.addEventListener("click", () => {
  chrome.runtime.sendMessage({ action: "clear_urls" }, () => {
    urlListEl.value = "";
  });
});

generateBtn.addEventListener("click", async () => {
  const urls = urlListEl.value
    .split(/\n+/)
    .map((url) => url.trim())
    .filter(Boolean);

  if (!urls.length) {
    alert("No URLs to generate citations for!");
    return;
  }

  chrome.runtime.sendMessage({ action: "set_urls", urls });

  const payload = {
    urls,
    style: styleEl.value,
    use_ai: useAiEl.checked,
  };

  try {
    const res = await fetch("http://localhost:8000/api/citations/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Backend returned ${res.status}`);
    }

    const text = await res.text();
    const dataUrl = "data:text/plain;charset=utf-8," + encodeURIComponent(text);

    chrome.downloads.download(
      { url: dataUrl, filename: "citations.txt", saveAs: false },
      () => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError.message);
          alert(`Download failed: ${chrome.runtime.lastError.message}`);
        }
      }
    );
  } catch (err) {
    console.error(err);
    alert("Error generating citations. Is the backend running?");
  }
});
