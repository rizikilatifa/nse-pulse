import { ExternalLink, TrendingUp, TrendingDown, Minus, Clock, Newspaper } from 'lucide-react'

const SentimentIcon = ({ label }) => {
  const config = {
    positive: { Icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-900/30' },
    negative: { Icon: TrendingDown, color: 'text-red-400', bg: 'bg-red-900/30' },
    neutral: { Icon: Minus, color: 'text-yellow-400', bg: 'bg-yellow-900/30' },
  }

  const { Icon, color, bg } = config[label] || config.neutral

  return (
    <div className={`p-2 rounded-lg ${bg}`}>
      <Icon className={`w-5 h-5 ${color}`} />
    </div>
  )
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'Unknown date'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function HeadlinesPanel({ sentimentData, loading }) {
  if (loading) {
    return (
      <div className="bg-gray-800/50 rounded-xl p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/3"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
          <div className="h-32 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  if (!sentimentData) {
    return null
  }

  const { ticker, company_name, sector, sentiment, top_headlines, last_updated } = sentimentData

  return (
    <div className="space-y-6">
      {/* Company Header */}
      <div className="bg-gray-800/50 rounded-xl p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-white">{ticker}</h2>
              <span className="text-xs px-2 py-1 bg-gray-700 rounded text-gray-300">
                {sector}
              </span>
            </div>
            <p className="text-gray-400 mt-1">{company_name}</p>
          </div>
          <div className="text-right">
            <SentimentIcon label={sentiment.label} />
            <p className="text-sm text-gray-400 mt-2 capitalize">
              {sentiment.label || 'No sentiment'}
            </p>
          </div>
        </div>

        {/* Sentiment Stats */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-700/50 rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase tracking-wide">Articles</p>
            <p className="text-2xl font-bold text-white mt-1">{sentiment.article_count}</p>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase tracking-wide">Confidence</p>
            <p className="text-2xl font-bold text-white mt-1">
              {sentiment.score ? `${(sentiment.score * 100).toFixed(1)}%` : '—'}
            </p>
          </div>
          <div className="bg-gray-700/50 rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase tracking-wide">Last Updated</p>
            <p className="text-sm font-medium text-white mt-1">
              {last_updated ? formatDate(last_updated) : 'Never'}
            </p>
          </div>
        </div>
      </div>

      {/* Headlines */}
      <div className="bg-gray-800/50 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <Newspaper className="w-5 h-5 text-gray-400" />
            <h3 className="text-lg font-semibold text-white">Top Headlines</h3>
          </div>
        </div>

        {top_headlines.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            <Newspaper className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No headlines available yet</p>
            <p className="text-sm mt-1">Click "Refresh Data" to scrape news articles</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-700">
            {top_headlines.map((headline, index) => (
              <a
                key={index}
                href={headline.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 hover:bg-gray-700/50 transition-colors group"
              >
                <div className="flex items-start gap-3">
                  <SentimentIcon label={headline.sentiment} />
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium group-hover:text-emerald-400 transition-colors">
                      {headline.headline}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                      <span>{headline.source}</span>
                      {headline.published_at && (
                        <>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(headline.published_at)}
                          </span>
                        </>
                      )}
                      {headline.score && (
                        <>
                          <span>•</span>
                          <span className="capitalize">{headline.sentiment}</span>
                          <span>({(headline.score * 100).toFixed(0)}%)</span>
                        </>
                      )}
                    </div>
                  </div>
                  <ExternalLink className="w-4 h-4 text-gray-500 group-hover:text-emerald-400 transition-colors flex-shrink-0" />
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default HeadlinesPanel
