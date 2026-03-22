import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const SentimentBadge = ({ label }) => {
  if (!label) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-700 text-gray-400">
        <Minus className="w-3 h-3" />
        No data
      </span>
    )
  }

  const config = {
    positive: {
      bg: 'bg-green-900/50',
      text: 'text-green-400',
      border: 'border-green-700',
      Icon: TrendingUp,
    },
    negative: {
      bg: 'bg-red-900/50',
      text: 'text-red-400',
      border: 'border-red-700',
      Icon: TrendingDown,
    },
    neutral: {
      bg: 'bg-yellow-900/50',
      text: 'text-yellow-400',
      border: 'border-yellow-700',
      Icon: Minus,
    },
  }

  const { bg, text, border, Icon } = config[label] || config.neutral

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${bg} ${text} border ${border}`}>
      <Icon className="w-3 h-3" />
      {label.charAt(0).toUpperCase() + label.slice(1)}
    </span>
  )
}

function TickerList({ tickers, selectedTicker, onSelect }) {
  return (
    <div className="bg-gray-800/50 rounded-xl overflow-hidden">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">NSE Top 10</h2>
        <p className="text-sm text-gray-400 mt-1">Click to view sentiment details</p>
      </div>
      <div className="divide-y divide-gray-700">
        {tickers.map((ticker) => (
          <button
            key={ticker.ticker}
            onClick={() => onSelect(ticker.ticker)}
            className={`w-full p-4 text-left hover:bg-gray-700/50 transition-colors ${
              selectedTicker === ticker.ticker ? 'bg-emerald-900/30 border-l-4 border-emerald-500' : ''
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-white text-lg">{ticker.ticker}</span>
                  <span className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300">
                    {ticker.sector}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mt-1">{ticker.name}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <SentimentBadge label={ticker.sentiment_label} />
                {ticker.article_count > 0 && (
                  <span className="text-xs text-gray-500">
                    {ticker.article_count} article{ticker.article_count !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </div>
            {ticker.sentiment_score !== null && ticker.sentiment_score !== undefined && (
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                  <span>Confidence</span>
                  <span>{(ticker.sentiment_score * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${
                      ticker.sentiment_label === 'positive' ? 'bg-green-500' :
                      ticker.sentiment_label === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${ticker.sentiment_score * 100}%` }}
                  />
                </div>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

export default TickerList
