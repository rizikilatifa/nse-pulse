const SentimentIndicator = ({ label, score }) => {
  const config = {
    positive: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      text: 'text-emerald-400',
      gradient: 'from-emerald-500 to-emerald-400',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      )
    },
    negative: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      text: 'text-red-400',
      gradient: 'from-red-500 to-red-400',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
        </svg>
      )
    },
    neutral: {
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
      text: 'text-amber-400',
      gradient: 'from-amber-500 to-amber-400',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
        </svg>
      )
    }
  }

  if (!label) {
    return (
      <div className="flex flex-col items-center gap-1 p-4 rounded-xl bg-white/5 border border-white/10">
        <svg className="w-6 h-6 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span className="text-xs text-white/30 font-mono">No sentiment</span>
      </div>
    )
  }

  const { bg, border, text, gradient, icon } = config[label] || config.neutral

  return (
    <div className={`flex flex-col items-center gap-1 p-4 rounded-xl ${bg} border ${border}`}>
      <div className={text}>{icon}</div>
      <span className={`text-xs font-mono uppercase tracking-wider ${text}`}>
        {label}
      </span>
      {score && (
        <span className={`text-lg font-bold bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
          {(score * 100).toFixed(0)}%
        </span>
      )}
    </div>
  )
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function HeadlinesPanel({ sentimentData }) {
  if (!sentimentData) return null

  const { ticker, company_name, sector, sentiment, top_headlines, last_updated } = sentimentData

  return (
    <div className="space-y-6">
      {/* Company Header Card */}
      <div className="glass-card rounded-2xl overflow-hidden">
        {/* Company info */}
        <div className="p-6">
          <div className="flex items-start justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className="font-mono text-3xl font-bold text-gradient">{ticker}</span>
                <span className="text-xs px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-white/50 font-mono uppercase tracking-wider">
                  {sector}
                </span>
              </div>
              <p className="text-white/60">{company_name}</p>
            </div>

            {/* Sentiment indicator */}
            <SentimentIndicator label={sentiment.label} score={sentiment.score} />
          </div>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-3 divide-x divide-white/5 border-t border-white/5">
          <div className="p-4 text-center">
            <p className="text-xs text-white/30 uppercase tracking-wider font-mono mb-1">Articles</p>
            <p className="text-2xl font-bold font-display text-white/90">{sentiment.article_count}</p>
          </div>
          <div className="p-4 text-center">
            <p className="text-xs text-white/30 uppercase tracking-wider font-mono mb-1">Confidence</p>
            <p className="text-2xl font-bold font-display text-white/90">
              {sentiment.score ? `${(sentiment.score * 100).toFixed(0)}%` : '—'}
            </p>
          </div>
          <div className="p-4 text-center">
            <p className="text-xs text-white/30 uppercase tracking-wider font-mono mb-1">Updated</p>
            <p className="text-sm font-mono text-white/60 mt-1">
              {last_updated ? formatDate(last_updated) : 'Never'}
            </p>
          </div>
        </div>
      </div>

      {/* Headlines Section */}
      <div className="glass-card rounded-2xl overflow-hidden">
        {/* Section header */}
        <div className="p-5 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#d69e2e]/10 flex items-center justify-center">
              <svg className="w-4 h-4 text-[#d69e2e]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <div>
              <h3 className="font-display font-semibold text-white">Recent Headlines</h3>
              <p className="text-xs text-white/40 font-mono">Financial news analysis</p>
            </div>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-white/40 font-mono">
            {top_headlines?.length || 0} articles
          </span>
        </div>

        {/* Headlines list */}
        {top_headlines?.length > 0 ? (
          <div className="divide-y divide-white/5">
            {top_headlines.map((headline, index) => {
              const sentimentColors = {
                positive: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', bar: 'bg-emerald-500' },
                negative: { bg: 'bg-red-500/10', text: 'text-red-400', bar: 'bg-red-500' },
                neutral: { bg: 'bg-amber-500/10', text: 'text-amber-400', bar: 'bg-amber-500' }
              }
              const colors = sentimentColors[headline.sentiment] || sentimentColors.neutral

              return (
                <a
                  key={index}
                  href={headline.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-5 hover:bg-white/[0.02] transition-all duration-200 group"
                >
                  <div className="flex gap-4">
                    {/* Sentiment indicator */}
                    <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${colors.bg} flex items-center justify-center`}>
                      <span className={`font-mono text-xs font-bold ${colors.text}`}>
                        {headline.sentiment === 'positive' ? '↑' : headline.sentiment === 'negative' ? '↓' : '→'}
                      </span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p className="text-white/80 font-medium leading-snug group-hover:text-white transition-colors">
                        {headline.headline}
                      </p>

                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-xs text-white/40">
                        <span className="inline-flex items-center gap-1.5">
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                          </svg>
                          {headline.source}
                        </span>
                        {headline.published_at && (
                          <span className="inline-flex items-center gap-1.5">
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {formatDate(headline.published_at)}
                          </span>
                        )}
                        {headline.score && (
                          <span className={`inline-flex items-center gap-1.5 ${colors.text}`}>
                            <span className="font-mono">{(headline.score * 100).toFixed(0)}%</span>
                            <span className="capitalize">{headline.sentiment}</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* External link icon */}
                    <svg className="w-4 h-4 text-white/20 group-hover:text-[#d69e2e] transition-colors flex-shrink-0 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </div>
                </a>
              )
            })}
          </div>
        ) : (
          <div className="p-12 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/5 flex items-center justify-center">
              <svg className="w-8 h-8 text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <p className="text-white/40 font-display">No headlines available</p>
            <p className="text-sm text-white/20 mt-1">Click "Sync News" to fetch latest articles</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default HeadlinesPanel
