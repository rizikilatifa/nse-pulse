const SentimentBadge = ({ label, score }) => {
  const config = {
    positive: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-400',
      icon: '↑',
      glow: 'shadow-emerald-500/20'
    },
    negative: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      text: 'text-red-400',
      icon: '↓',
      glow: 'shadow-red-500/20'
    },
    neutral: {
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
      icon: '→',
      glow: 'shadow-amber-500/20'
    }
  }

  if (!label) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono bg-white/5 border border-white/10 text-white/40">
        <span className="w-1.5 h-1.5 rounded-full bg-white/20" />
        No data
      </span>
    )
  }

  const { bg, border, text, icon, glow } = config[label] || config.neutral

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono ${bg} ${border} border ${text} shadow-sm ${glow}`}>
      <span className="font-bold">{icon}</span>
      {label.charAt(0).toUpperCase() + label.slice(1)}
    </span>
  )
}

function TickerList({ tickers, selectedTicker, onSelect }) {
  // Count articles with sentiment
  const activeCount = tickers.filter(t => t.article_count > 0).length

  return (
    <div className="glass-card rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-white/5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-lg font-semibold text-white">NSE Top 10</h2>
            <p className="text-xs text-white/40 mt-0.5 font-mono">
              {activeCount} stocks with sentiment data
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-white/30 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live
          </div>
        </div>
      </div>

      {/* Ticker Grid */}
      <div className="p-3">
        <div className="grid gap-2">
          {tickers.map((ticker, index) => {
            const isSelected = selectedTicker === ticker.ticker
            const hasData = ticker.article_count > 0

            return (
              <button
                key={ticker.ticker}
                onClick={() => onSelect(ticker.ticker)}
                className={`
                  relative group p-4 rounded-xl text-left transition-all duration-300
                  ${isSelected
                    ? 'bg-gradient-to-r from-[#d69e2e]/20 to-[#d69e2e]/5 border border-[#d69e2e]/30 shadow-lg shadow-[#d69e2e]/10'
                    : 'bg-white/[0.02] hover:bg-white/[0.05] border border-transparent hover:border-white/10'
                  }
                `}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {/* Selection indicator */}
                {isSelected && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-[#d69e2e] rounded-full" />
                )}

                <div className="flex items-start justify-between gap-4">
                  {/* Left side - Ticker info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      {/* Ticker symbol */}
                      <span className={`
                        font-mono text-lg font-bold tracking-tight
                        ${isSelected ? 'text-[#d69e2e]' : 'text-white/90 group-hover:text-white'}
                        transition-colors
                      `}>
                        {ticker.ticker}
                      </span>
                      {/* Sector tag */}
                      <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-white/40 font-mono uppercase tracking-wider">
                        {ticker.sector?.slice(0, 4)}
                      </span>
                    </div>
                    {/* Company name */}
                    <p className="text-sm text-white/40 truncate mt-1 group-hover:text-white/50 transition-colors">
                      {ticker.name}
                    </p>
                  </div>

                  {/* Right side - Sentiment */}
                  <div className="flex flex-col items-end gap-2">
                    <SentimentBadge label={ticker.sentiment_label} score={ticker.sentiment_score} />
                    {hasData && (
                      <span className="text-[10px] text-white/30 font-mono">
                        {ticker.article_count} {ticker.article_count === 1 ? 'article' : 'articles'}
                      </span>
                    )}
                  </div>
                </div>

                {/* Confidence bar */}
                {hasData && ticker.sentiment_score !== null && (
                  <div className="mt-3 space-y-1">
                    <div className="flex justify-between text-[10px] font-mono text-white/30">
                      <span>Confidence</span>
                      <span>{(ticker.sentiment_score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className={`
                          h-full rounded-full transition-all duration-500
                          ${ticker.sentiment_label === 'positive' ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' :
                            ticker.sentiment_label === 'negative' ? 'bg-gradient-to-r from-red-500 to-red-400' :
                            'bg-gradient-to-r from-amber-500 to-amber-400'}
                        `}
                        style={{ width: `${ticker.sentiment_score * 100}%` }}
                      />
                    </div>
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default TickerList
