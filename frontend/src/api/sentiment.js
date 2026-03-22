const API_BASE = import.meta.env.VITE_API_URL || ''

export async function fetchTickers() {
  const response = await fetch(`${API_BASE}/api/tickers`)
  if (!response.ok) {
    throw new Error(`Failed to fetch tickers: ${response.statusText}`)
  }
  return response.json()
}

export async function fetchSentiment(ticker) {
  const response = await fetch(`${API_BASE}/api/sentiment/${ticker}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch sentiment: ${response.statusText}`)
  }
  return response.json()
}

export async function triggerScrape() {
  const response = await fetch(`${API_BASE}/api/scrape`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error(`Failed to trigger scrape: ${response.statusText}`)
  }
  return response.json()
}
