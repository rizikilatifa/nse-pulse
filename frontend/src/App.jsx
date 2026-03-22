import { useState, useEffect } from 'react'
import TickerList from './components/TickerList'
import HeadlinesPanel from './components/HeadlinesPanel'
import { fetchTickers, fetchSentiment, triggerScrape } from './api/sentiment'

function App() {
  const [tickers, setTickers] = useState([])
  const [selectedTicker, setSelectedTicker] = useState(null)
  const [sentimentData, setSentimentData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scrapeLoading, setScrapeLoading] = useState(false)
  const [lastScraped, setLastScraped] = useState(null)

  useEffect(() => {
    loadTickers()
  }, [])

  const loadTickers = async () => {
    setLoading(true)
    try {
      const data = await fetchTickers()
      setTickers(data.tickers)
      setLastScraped(data.last_scraped)
    } catch (error) {
      console.error('Failed to load tickers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectTicker = async (ticker) => {
    setSelectedTicker(ticker)
    setSentimentData(null)
    try {
      const data = await fetchSentiment(ticker)
      setSentimentData(data)
    } catch (error) {
      console.error('Failed to load sentiment:', error)
    }
  }

  const handleScrape = async () => {
    setScrapeLoading(true)
    try {
      await triggerScrape()
      await loadTickers()
      if (selectedTicker) {
        const data = await fetchSentiment(selectedTicker)
        setSentimentData(data)
      }
    } catch (error) {
      console.error('Failed to scrape:', error)
    } finally {
      setScrapeLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleString('en-KE', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a1628] via-[#1a365d] to-[#0f1f3a] text-white">
      {/* Noise texture overlay */}
      <div className="fixed inset-0 opacity-[0.02] pointer-events-none z-0"
           style={{backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25 height='100%25 filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")"}} />

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-20 border-b border-white/10 bg-[#0a1628]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Branding */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#d69e2e] to-[#b7791f] flex items-center justify-center shadow-lg shadow-[#d69e2e]/20">
                  <span className="font-display text-xl font-bold text-[#0a1628]">N</span>
                </div>
                <div className="absolute -inset-1 bg-gradient-to-r from-[#d69e2e]/20 to-transparent rounded-xl blur-sm -z-10" />
              </div>
              <div>
                <h1 className="font-display text-xl sm:text-2xl font-bold tracking-tight leading-tight">
                  <span className="text-gradient">NSE</span> <span className="text-white/90">Pulse</span>
                </h1>
                <p className="hidden sm:block text-xs text-white/50 font-mono tracking-wider uppercase">
                  Real-time Sentiment Analysis
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              {lastScraped && (
                <div className="hidden md:flex items-center gap-2 text-xs text-white/40 font-mono">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Last sync: {formatDate(lastScraped)}
                </div>
              )}
              <button
                onClick={handleScrape}
                disabled={scrapeLoading}
                className="group relative px-4 py-2 rounded-lg font-medium text-sm overflow-hidden transition-all duration-300 disabled:opacity-50"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-[#d69e2e] via-[#ecc94b] to-[#d69e2e] opacity-100 group-hover:opacity-90 transition-opacity" />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                <span className="relative text-[#0a1628] font-semibold">
                  {scrapeLoading ? (
                    <span className="flex items-center gap-2">
                      <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Syncing...
                    </span>
                  ) : (
                    'Sync News'
                  )}
                </span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-full border-2 border-[#d69e2e]/30 border-t-[#d69e2e] animate-spin" />
              <p className="text-white/50 font-mono text-sm">Loading market data...</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Ticker List - Left Column */}
            <div className="lg:col-span-5 stagger-1">
              <TickerList
                tickers={tickers}
                selectedTicker={selectedTicker}
                onSelect={handleSelectTicker}
              />
            </div>

            {/* Sentiment Detail - Right Column */}
            <div className="lg:col-span-7 stagger-2">
              {selectedTicker ? (
                sentimentData ? (
                  <HeadlinesPanel sentimentData={sentimentData} />
                ) : (
                  <div className="flex items-center justify-center h-64 glass-card rounded-2xl">
                    <div className="w-8 h-8 rounded-full border-2 border-[#d69e2e]/30 border-t-[#d69e2e] animate-spin" />
                  </div>
                )
              ) : (
                <div className="glass-card rounded-2xl p-8 text-center">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-white/5 flex items-center justify-center">
                    <svg className="w-10 h-10 text-[#d69e2e]/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4m6 6v-1a4 4 0 00-8 0v-1c0-1.657.343-3 2-3h6z" />
                    </svg>
                  </div>
                  <h3 className="font-display text-xl text-white/60 mb-2">Select a Stock</h3>
                  <p className="text-sm text-white/40 max-w-sm mx-auto">
                    Choose a ticker from the list to view detailed sentiment analysis and recent headlines
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/30 font-mono">
            <p>Powered by FinBERT NLP Engine</p>
            <p>NSE Pulse © 2026</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
