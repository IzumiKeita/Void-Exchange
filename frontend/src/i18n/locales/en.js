export default {
  dashboard: {
    title: "🚀 Void Exchange",
    trends: "🔥 View Trends",
    voidTrader: "💠 Void Trader",
    ducats: "💰 Ducats/Plat",
    vault: "🏛️ Prime Vault",
    trading: "📈 Trading Advisor",
    searchPlaceholder: "Search item...",
    sort: {
      down: "📉 Price Drop",
      up: "📈 Price Rise",
      highPrice: "💰 Highest Price",
      downTitle: "Ascending order: Show items that dropped in price first (Negative Trend)",
      upTitle: "Descending order: Show items that rose in price first (Positive Trend)",
      highPriceTitle: "Descending order: Highest price to lowest"
    },
    tabs: {
      recent: "Recent",
      warframes: "Warframes",
      primary: "Primary",
      secondary: "Secondary",
      melee: "Melee",
      mods: "Mods",
      arcanes: "Arcanes",
      relics: "Relics",
      others: "Others"
    },
    subfilters: {
      all: "All",
      sets: "Sets",
      blueprints: "Blueprints",
      neuroptics: "Neuroptics",
      chassis: "Chassis",
      systems: "Systems",
      receiver: "Receiver",
      barrel: "Barrel",
      stock: "Stock",
      blade: "Blade",
      handle: "Handle"
    },
    card: {
      rank: "Rank",
      min: "Min",
      avg: "Avg",
      max: "Max",
      vol: "Vol:"
    },
    history: {
      clear: "Clear History",
      empty: "No recently viewed items.",
      emptySub: "Browse other tabs to check items."
    },
    pagination: {
      prev: "Previous",
      next: "Next",
      page: "Page {current} of {total}"
    }
  },
  voidTrader: {
    title: "💠 Void Trader (Baro Ki'Teer)",
    status: {
      active: "ACTIVE",
      away: "AWAY"
    },
    loading: "Consulting the Void...",
    location: "Location",
    unknown: "Unknown",
    departingIn: "Departing in",
    arrivingIn: "Arriving in",
    inventory: {
      current: "Current Inventory",
      last: "Last Visit",
      inactiveNotice: "Baro is away. Showing inventory from his last visit.",
      empty: "Baro Ki'Teer is traveling the Void. No recent data available."
    },
    history: {
      title: "Full History",
      toggleHide: "Hide History",
      toggleShow: "View Previous History",
      loading: "Loading history...",
      empty: "No history available with current filters.",
      tradeableItems: "tradeable items",
      noItemsCategory: "No items in this category."
    },
    table: {
      item: "Item",
      ducats: "Ducats",
      credits: "Credits",
      plat: "Platinum (Hist.)"
    },
    filters: {
      all: "All",
      mods: "Mods",
      weapons: "Weapons",
      relics: "Relics",
      others: "Others"
    },
    market: {
      minPrice: "Min Price:",
      avg: "Avg:",
      noData: "No market data"
    },
    actions: {
      refresh: "Refresh data"
    }
  },
  itemDetail: {
    loading: "Loading market information...",
    stats: {
      minPrice: "Minimum Price",
      avgPrice: "Average Price",
      ducats: "Ducats Value",
      volume: "Volume (48h)"
    },
    tags: {
      vaulted: "Vaulted",
      resurgence: "Prime Resurgence"
    },
    chart: {
      title: "Price History",
      rank: "Rank {rank}",
      maxRank: "Max (R{rank})",
      periods: {
        "90d": "90 Days",
        "48h": "48 Hours",
        "24h": "24 Hours"
      },
      noData: "No historical data available"
    },
    orders: {
      sellers: "Sellers",
      buyers: "Buyers",
      whisper: "Message",
      quantity: "x{qty}",
      reputation: "Rep: {rep}"
    },
    tags: {
      mr: "MR",
      vaulted: "Vaulted",
      resurgence: "Prime Resurgence"
    },
    units: {
      plat: "Pt",
      ducats: "Ducats"
    }
  },
  common: {
    loading: "Loading...",
    error: "Error",
    retry: "Retry",
    noData: "No data available"
  },
  trends: {
    title: "🔥 Market Trends",
    subtitle: "Most requested items in the last 24 hours",
    sell: "📉 Supply (Sellers)",
    buy: "📈 Demand (Buyers)",
    loading: "Analyzing market... (This may take a few moments)",
    empty: "No items in this category or no data available.",
    table: {
      rank: "#",
      item: "Item",
      trend: "Trend",
      volume: "Volume (24h)"
    },
    indicators: {
      up: "▲ Up",
      down: "▼ Down",
      new: "★ New",
      same: "= Stable"
    }
  },
  ducats: {
    title: "💰 Ducats vs Platinum",
    subtitle: "Find the best items to convert to Ducats or sell for Platinum",
    searchPlaceholder: "Search item...",
    loading: "Consulting Baro Ki'Teer... (Loading data)",
    error: "Could not load Ducanator data. Please try again later.",
    empty: "No items found matching your search.",
    table: {
      item: "Item",
      ducats: "Ducats ↕",
      plat: "Platinum (WA) ↕",
      ratio: "Ducats/Plat ↕",
      volume: "Volume ↕"
    }
  },
  vault: {
    title: "🏛️ Prime Vault Analysis: Warframes",
    titleWeapons: "🏛️ Prime Vault Analysis: Weapons",
    backDashboard: "⬅ Back to Dashboard",
    nav: {
      warframes: "Warframes",
      weapons: "Weapons"
    },
    loading: "Analyzing void state...",
    loadingWeapons: "Analyzing void arsenal...",
    items: "Items",
    sections: {
      active: {
        title: "✅ Active (Farmable)",
        desc: "These Warframes can currently be obtained by opening new relics.",
        descWeapons: "Weapons that can currently be obtained by opening new relics."
      },
      resurgence: {
        title: "🔄 Prime Resurgence (Varzia)",
        desc: "Temporarily available at Maroo's Bazaar in exchange for Aya/Regal Aya.",
        descWeapons: "Weapons temporarily available at Maroo's Bazaar."
      },
      vaulted: {
        title: "🔒 Vaulted",
        desc: "Relics for these items cannot be obtained (trading only).",
        descWeapons: "Weapons retired. Only available via trading."
      }
    },
    searchPlaceholder: "Search in Vault...",
    searchPlaceholderWeapons: "Search vaulted weapon...",
    cards: {
      warning: "⚠ Vaulting Soon",
      viewMarket: "View Market",
      view: "View"
    }
  },
  chat: {
    title: "Warframe Trading Assistant",
    subtitle: "Your expert in the origin system economy",
    placeholder: "Ask about prices, items, relics...",
    typing: "Typing...",
    welcome: "Hello! I am your full-screen Warframe trading expert. How can I help you?",
    user: "You",
    bot: "Assistant",
    toggle: "💬 AI Chat",
    windowTitle: "Trading Assistant ↗",
    errorGeneric: "Sorry, there was an error processing your message.",
    errorServer: "Server error: {error}",
    errorConnection: "Connection error: Could not contact server."
  },
  trading: {
    title: "📈 Trading & Platinum Advisor",
    subtitle: "Advanced tools to maximize your Platinum profits.",
    tabs: {
      ducats: "💰 Ducats / Platinum",
      investment: "🏦 Investments (Vault)"
    },
    strategies: {
      sellTrash: "Sell Trash (Get Plat)",
      buyBaro: "Buy for Baro (Get Ducats)",
      sellDesc: "Items that give <strong>few ducats</strong> but are worth <strong>lots of platinum</strong>. Don't burn them! Sell them.",
      buyDesc: "Items that cost <strong>little platinum</strong> but give <strong>lots of ducats</strong>. Buy cheap to burn."
    },
    loading: "Loading market data...",
    table: {
      item: "Item",
      price: "Price (Plat)",
      ducats: "Ducats",
      ratio: "Ratio (Duc/Plat)",
      action: "Action",
      viewMarket: "View Market"
    },
    investment: {
      title: "🏛️ Investment Opportunities",
      desc: "Items soon to enter the Vault. Their price will rise when they stop dropping.",
      loading: "Analyzing Vault state...",
      badge: "VAULTING SOON",
      action: "Buy / Farm",
      empty: "No items marked as 'Vaulting Soon' at this moment."
    },
    modal: {
      loading: "Loading complete data...",
      components: "Set Components",
      stats: {
        volume: "Volume (48h)",
        min: "Minimum",
        max: "Maximum",
        avg: "Average"
      },
      chartTitle: "Price and Volume Trend (90 days)",
      sellers: "Sellers",
      buyers: "Buyers",
      ai: {
        analyze: "🧠 AI Analysis",
        analyzing: "🔄 Analyzing..."
      },
      viewMarket: "View on Warframe.market ↗",
      errorAnalysis: "Error analyzing item.",
      chart: {
        avgPrice: "Average Price",
        plat: "Platinum",
        volume: "Volume",
        maxRank: "Max Rank",
        intact: "Intact"
      }
    }
  }
}
