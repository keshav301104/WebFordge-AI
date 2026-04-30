const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

export const startGeneration = async (landingPageUrl, adFile, adUrl, customPrompt) => {
  const formData = new FormData();
  formData.append("landing_page_url", landingPageUrl);
  
  if (adFile) formData.append("file", adFile);
  else if (adUrl) formData.append("ad_creative_url", adUrl);
  
  // Append the new custom prompt if the user typed one
  if (customPrompt) formData.append("custom_prompt", customPrompt);

  const response = await fetch(`${BACKEND_URL}/api/generate`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) throw new Error("Backend connection failed");
  return response.json();
};

export const checkJobStatus = async (jobId) => {
  const response = await fetch(`${BACKEND_URL}/api/status/${jobId}`);
  if (!response.ok) throw new Error("Status check failed");
  return response.json();
};