const STORAGE_KEY = "citeEverythingForMe.urls";

const readStorage = () =>
  new Promise((resolve) => {
    chrome.storage.local.get([STORAGE_KEY], (result) => {
      const urls = Array.isArray(result[STORAGE_KEY]) ? result[STORAGE_KEY] : [];
      resolve(urls);
    });
  });

const writeStorage = (urls) =>
  new Promise((resolve) => {
    chrome.storage.local.set({ [STORAGE_KEY]: urls }, () => resolve(urls));
  });

export const getStoredUrls = async () => {
  const urls = await readStorage();
  return urls;
};

export const addUrlToStorage = async (url) => {
  const urls = await readStorage();
  if (urls.includes(url)) {
    return urls;
  }
  const updated = [...urls, url];
  return writeStorage(updated);
};

export const removeUrlFromStorage = async (url) => {
  const urls = await readStorage();
  const updated = urls.filter((entry) => entry !== url);
  return writeStorage(updated);
};

export const clearStoredUrls = async () => writeStorage([]);



