const API_ENDPOINT = "http://localhost:8000/generate";

export const generateCitations = async (urls, format) => {
  const response = await fetch(API_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      urls,
      format,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Citation generation failed.");
  }

  const payload = await response.json();
  if (!Array.isArray(payload.citations)) {
    throw new Error("Backend returned an unexpected response.");
  }

  return payload.citations;
};



