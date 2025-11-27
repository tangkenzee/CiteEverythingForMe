import {
  addUrlToStorage,
  clearStoredUrls,
  getStoredUrls,
  removeUrlFromStorage,
} from "./utils/storage.js";
import { generateCitations } from "./utils/api.js";

const STORAGE_LIMIT = 5;
const addUrlButton = document.getElementById("add-url-button");
const clearUrlsButton = document.getElementById("clear-urls-button");
const generateButton = document.getElementById("generate-button");
const urlList = document.getElementById("url-list");
const statusEl = document.getElementById("status");
const styleSelect = document.getElementById("format-select");

const setStatus = (message, error = false) => {
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.style.color = error ? "#c53030" : "#0b1f3a";
};

const renderUrls = (urls) => {
  if (!urlList) return;
  urlList.innerHTML = "";

  if (!urls.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "No URLs saved yet.";
    urlList.append(empty);
    return;
  }

  urls.forEach((url) => {
    const item = document.createElement("li");
    const text = document.createElement("span");
    text.textContent = url;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Remove";
    remove.addEventListener("click", async () => {
      const updated = await removeUrlFromStorage(url);
      renderUrls(updated);
      setStatus("URL removed.");
    });

    item.append(text, remove);
    urlList.append(item);
  });
};

const syncAndRender = async () => {
  const urls = await getStoredUrls();
  renderUrls(urls);
};

const handleAddUrl = () => {
  if (!chrome.tabs) {
    setStatus("Unable to access tabs API.", true);
    return;
  }

  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    const current = tabs[0];
    const url = current?.url;

    if (!url) {
      setStatus("No active tab URL found.", true);
      return;
    }

    const urls = await getStoredUrls();
    if (urls.length >= STORAGE_LIMIT) {
      setStatus("You can store up to 5 URLs.", true);
      return;
    }

    const updated = await addUrlToStorage(url);
    renderUrls(updated);
    setStatus("URL saved.");
  });
};

const handleClear = async () => {
  await clearStoredUrls();
  renderUrls([]);
  setStatus("All URLs cleared.");
};

const buildInTextCitation = (citation) => {
  const authorYearMatch = citation.match(/^([^.(]+?)\s*\((\d{4})\)/);
  if (authorYearMatch) {
    const author = authorYearMatch[1].trim();
    const year = authorYearMatch[2];
    return `(${author}, ${year})`;
  }
  const yearMatch = citation.match(/\b(19|20)\d{2}\b/);
  if (yearMatch) {
    return `(${yearMatch[0]})`;
  }
  return '';
};

const downloadCitations = (citations) => {
  const formatted = citations
    .map((citation, index) => {
      const number = `${index + 1}.`;
      const intext = buildInTextCitation(citation);
      return `${number}\nIn-text citation:\n${intext}\nReference:\n${citation}\n`;
    })
    .join("\n");

  const blob = new Blob([formatted], { type: "text/plain" });
  const downloadUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = downloadUrl;
  anchor.download = "citations.txt";
  anchor.click();
  URL.revokeObjectURL(downloadUrl);
};

const handleGenerate = async () => {
  setStatus("Generating citations...");
  if (generateButton) generateButton.disabled = true;

  try {
    const urls = await getStoredUrls();
    if (!urls.length) {
      setStatus("Add at least one URL before generating.", true);
      return;
    }

    if (urls.length > STORAGE_LIMIT) {
      setStatus("Maximum 5 URLs allowed. Remove extras.", true);
      return;
    }

    const formatValue = styleSelect?.value ?? "harvard";
    const citations = await generateCitations(urls, formatValue);
    downloadCitations(citations);
    setStatus(`Downloaded ${citations.length} citations.`);
  } catch (error) {
    console.error(error);
    setStatus(error?.message ?? "Failed to generate citations.", true);
  } finally {
    if (generateButton) generateButton.disabled = false;
  }
};

addUrlButton?.addEventListener("click", handleAddUrl);
clearUrlsButton?.addEventListener("click", handleClear);
generateButton?.addEventListener("click", handleGenerate);

syncAndRender();

