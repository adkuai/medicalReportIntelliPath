const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function analyzeDocument(file, customColabUrl = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (customColabUrl) {
    formData.append('custom_colab_url', customColabUrl.trim());
  }

  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMsg = `Server error ${response.status}`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (e) {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return await response.json();
}

export async function checkColabStatus(customColabUrl = null) {
  let url = `${API_BASE}/status`;
  if (customColabUrl) {
    url += `?colab_url=${encodeURIComponent(customColabUrl.trim())}`;
  }

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to check Colab status (${response.status})`);
  }
  return await response.json();
}

export async function fetchSampleData() {
  const response = await fetch(`${API_BASE}/sample`);
  if (!response.ok) {
    throw new Error(`Failed to load sample dataset (${response.status})`);
  }
  return await response.json();
}

