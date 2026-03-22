import { useState, useEffect } from 'react'
import { TrendingUp, RefreshCw, AlertCircle } from 'lucide-react'
import TickerList from './components/TickerList'
import HeadlinesPanel from './components/HeadlinesPanel'
import { fetchTickers, fetchSentiment, triggerScrape } from './api/sentiment'

function App() {
  const [tickers, setTickers] = useState([])
  const [selectedTicker, setSelectedTicker] = useState(null)
  const [sentimentData, setSentimentData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [scraping, setScraping] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadTickers()
  }, [])

  useEffect(() => {
    if (selectedTicker) {
      loadSentiment(selectedTicker)
    }
  }, [selectedTicker])

  const loadTickers = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchTickers()
      setTickers(data.tickers)
    } catch (err) {
      setError('Failed to load tickers. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadSentiment = async (ticker) => {
    try {
      const data = await fetchSentiment(ticker)
      setSentimentData(data)
    } catch (err) {
      console.error('Failed to load sentiment:', err)
    }
  }

  const handleScrape = async () => {
    try {
      setScraping(true)
      const result = await triggerScrape()
      // Reload tickers after scrape
      await loadTickers()
      if (selectedTicker) {
        await loadSentiment(selectedTicker)
      }
      alert(`Scraped ${result.articles_scraped} articles, processed ${result.articles_processed}`)
    } catch (err) {
      alert('Scraping failed. Check the backend logs.')
      console.error(err)
    } finally {
      setScraping(false)
    }
  }

  const handleSelectTicker = (ticker) => {
    setSelectedTicker(ticker)
    setSentimentData(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-700 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-2 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">NSE Pulse</h1>
                <p className="text-xs text-gray-400">Real-time Sentiment Analysis</p>
              </div>
            </div>
            <button
              onClick={handleScrape}
              disabled={scraping}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-600 rounded-lg text-white font-medium transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
              {scraping ? 'Scraping...' : 'Refresh Data'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-700 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-200">{error}</span>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Ticker List */}
            <div className="lg:col-span-1">
              <TickerList
                tickers={tickers}
                selectedTicker={selectedTicker}
                onSelect={handleSelectTicker}
              />
            </div>

            {/* Headlines Panel */}
            <div className="lg:col-span-2">
              {selectedTicker ? (
                <HeadlinesPanel
                  sentimentData={sentimentData}
                  loading={!sentimentData && selectedTicker}
                />
              ) : (
                <div className="bg-gray-800/50 rounded-xl p-8 text-center">
                  <div className="text-gray-400">
                    <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">Select a ticker to view sentiment analysis</p>
                    <p className="text-sm mt-2">Click on any stock from the list</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-700 mt-8 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          NSE Pulse — Sentiment Analysis for Nairobi Securities Exchange
        </div>
      </footer>
    </div>
  )
}

export default App
