const STORAGE_KEY = "citeEverythingForMe.urls";

const ensureStorageInitialized = () => {
  chrome.storage.local.get([STORAGE_KEY], (result) => {
    if (!Array.isArray(result[STORAGE_KEY])) {
      chrome.storage.local.set({ [STORAGE_KEY]: [] });
    }
  });
};

chrome.runtime.onInstalled.addListener(ensureStorageInitialized);
chrome.runtime.onStartup.addListener(ensureStorageInitialized);

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === "SYNC_URLS") {
    chrome.storage.local.get([STORAGE_KEY], (result) => {
      sendResponse({
        urls: Array.isArray(result[STORAGE_KEY]) ? result[STORAGE_KEY] : [],
      });
    });
    return true;
  }
});


