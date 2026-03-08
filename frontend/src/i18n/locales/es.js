export default {
  dashboard: {
    title: "🚀 Void Exchange",
    trends: "🔥 Ver Tendencias",
    voidTrader: "💠 Void Trader",
    ducats: "💰 Ducados/Plat",
    vault: "🏛️ Bóveda Prime",
    trading: "📈 Trading Advisor",
    searchPlaceholder: "Buscar item...",
    sort: {
      down: "📉 Bajada",
      up: "📈 Subida",
      highPrice: "💰 Mayor Precio",
      downTitle: "Orden ascendente: Mostrar primero los ítems que han bajado de precio (Tendencia Negativa)",
      upTitle: "Orden descendente: Mostrar primero los ítems que han subido de precio (Tendencia Positiva)",
      highPriceTitle: "Orden descendente: Mayor precio a menor"
    },
    tabs: {
      recent: "Recientes",
      warframes: "Warframes",
      primary: "Primarias",
      secondary: "Secundarias",
      melee: "Melee",
      mods: "Mods",
      arcanes: "Arcanos",
      relics: "Reliquias",
      others: "Otros"
    },
    subfilters: {
      all: "Todo",
      sets: "Sets",
      blueprints: "Planos",
      neuroptics: "Neurópticas",
      chassis: "Chasis",
      systems: "Sistemas",
      receiver: "Receptor",
      barrel: "Cañón",
      stock: "Culata",
      blade: "Hoja",
      handle: "Empuñadura"
    },
    card: {
      rank: "Rango",
      min: "Min",
      avg: "Med",
      max: "Max",
      vol: "Vol:"
    },
    history: {
      clear: "Limpiar Historial",
      empty: "No hay elementos vistos recientemente.",
      emptySub: "Navega por las otras pestañas para consultar items."
    },
    pagination: {
      prev: "Anterior",
      next: "Siguiente",
      page: "Página {current} de {total}"
    }
  },
  voidTrader: {
    title: "Void Trader (Baro Ki'Teer)",
    status: {
      active: "ACTIVO",
      away: "AUSENTE"
    },
    loading: "Consultando al Vacío...",
    location: "Ubicación",
    unknown: "Desconocida",
    departingIn: "Se marcha en",
    arrivingIn: "Llega en",
    inventory: {
      current: "Inventario Actual",
      last: "Última Visita",
      inactiveNotice: "Baro no está presente. Se muestra el inventario de su última visita.",
      empty: "Baro Ki'Teer está viajando por el Vacío. No hay datos recientes disponibles."
    },
    history: {
      title: "Historial Completo",
      toggleHide: "Ocultar Historial",
      toggleShow: "Ver Historial Anterior",
      loading: "Cargando historial...",
      empty: "No hay historial disponible con los filtros actuales.",
      tradeableItems: "ítems tradeables",
      noItemsCategory: "No hay ítems en esta categoría."
    },
    table: {
      item: "Ítem",
      ducats: "Ducados",
      credits: "Créditos",
      plat: "Platino (Hist.)"
    },
    filters: {
      all: "Todos",
      mods: "Mods",
      weapons: "Armas",
      relics: "Reliquias",
      others: "Otros"
    },
    market: {
      minPrice: "Precio Min:",
      avg: "Promedio:",
      noData: "Sin datos de mercado"
    },
    actions: {
      refresh: "Actualizar datos"
    }
  },
  itemDetail: {
    loading: "Cargando información del mercado...",
    stats: {
      minPrice: "Precio Mínimo",
      avgPrice: "Precio Promedio",
      ducats: "Valor en Ducados",
      volume: "Volumen (48h)"
    },
    tags: {
      vaulted: "Vaulted",
      resurgence: "Prime Resurgence"
    },
    chart: {
      title: "Historial de Precios",
      rank: "Rango {rank}",
      maxRank: "Max (R{rank})",
      periods: {
        "90d": "90 Días",
        "48h": "48 Horas",
        "24h": "24 Horas"
      },
      noData: "No hay datos históricos disponibles"
    },
    orders: {
      sellers: "Vendedores (Sell)",
      buyers: "Compradores (Buy)",
      whisper: "Mensaje",
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
      ducats: "Ducados"
    }
  },
  common: {
    loading: "Cargando...",
    error: "Error",
    retry: "Reintentar",
    noData: "No hay datos disponibles"
  },
  trends: {
    title: "🔥 Tendencias de Mercado",
    subtitle: "Items más solicitados en las últimas 24 horas",
    sell: "📉 Oferta (Ventas)",
    buy: "📈 Demanda (Compras)",
    loading: "Analizando el mercado... (Esto puede tomar unos momentos)",
    empty: "No hay items en esta categoría o no hay datos disponibles.",
    table: {
      rank: "#",
      item: "Item",
      trend: "Tendencia",
      volume: "Volumen (24h)"
    },
    indicators: {
      up: "▲ Sube",
      down: "▼ Baja",
      new: "★ Nuevo",
      same: "= Mantiene"
    }
  },
  ducats: {
    title: "💰 Ducados vs Platino",
    subtitle: "Encuentra los mejores items para convertir en Ducados o vender por Platino",
    searchPlaceholder: "Buscar item...",
    loading: "Consultando a Baro Ki'Teer... (Cargando datos)",
    error: "No se pudo cargar la información de Ducanator. Inténtalo de nuevo más tarde.",
    empty: "No se encontraron items que coincidan con la búsqueda.",
    table: {
      item: "Item",
      ducats: "Ducados ↕",
      plat: "Platino (WA) ↕",
      ratio: "Ducados/Plat ↕",
      volume: "Volumen ↕"
    }
  },
  vault: {
    title: "🏛️ Análisis de Bóveda Prime: Warframes",
    titleWeapons: "🏛️ Análisis de Bóveda Prime: Armas",
    backDashboard: "⬅ Volver al Dashboard",
    nav: {
      warframes: "Warframes",
      weapons: "Armas"
    },
    loading: "Analizando estado del vacío...",
    loadingWeapons: "Analizando arsenal del vacío...",
    items: "Items",
    sections: {
      active: {
        title: "✅ Activos (Farmables)",
        desc: "Estos Warframes se pueden conseguir actualmente abriendo reliquias nuevas.",
        descWeapons: "Armas que se pueden conseguir actualmente abriendo reliquias nuevas."
      },
      resurgence: {
        title: "🔄 Resurgimiento Prime (Varzia)",
        desc: "Disponibles temporalmente en el Bazar de Maroo a cambio de Aya/Aya Real.",
        descWeapons: "Armas disponibles temporalmente en el Bazar de Maroo."
      },
      vaulted: {
        title: "🔒 Bóveda (Vaulted)",
        desc: "No se pueden conseguir reliquias de estos items (solo comercio).",
        descWeapons: "Armas retiradas. Solo disponibles por comercio."
      }
    },
    searchPlaceholder: "Buscar en Bóveda...",
    searchPlaceholderWeapons: "Buscar arma vaulted...",
    cards: {
      warning: "⚠ Próximo a irse",
      viewMarket: "Ver Mercado",
      view: "Ver"
    }
  },
  chat: {
    title: "Asistente de Trading de Warframe",
    subtitle: "Tu experto en economía del sistema origen",
    placeholder: "Pregunta sobre precios, items, reliquias...",
    typing: "Escribiendo...",
    welcome: "¡Hola! Soy tu experto en trading de Warframe a pantalla completa. ¿En qué puedo ayudarte?",
    user: "Tú",
    bot: "Asistente",
    toggle: "💬 Chat IA",
    windowTitle: "Asistente de Trading ↗",
    errorGeneric: "Lo siento, hubo un error al procesar tu mensaje.",
    errorServer: "Error del servidor: {error}",
    errorConnection: "Error de conexión: No se pudo contactar con el servidor."
  },
  trading: {
    title: "📈 Asesor de Trading & Platino",
    subtitle: "Herramientas avanzadas para maximizar tus ganancias de Platino.",
    tabs: {
      ducats: "💰 Ducados / Platino",
      investment: "🏦 Inversiones (Vault)"
    },
    strategies: {
      sellTrash: "Vender Basura (Conseguir Plat)",
      buyBaro: "Comprar para Baro (Conseguir Ducados)",
      sellDesc: "Items que dan <strong>pocos ducados</strong> pero valen <strong>mucho platino</strong>. ¡No los quemes en Baro! Véndelos.",
      buyDesc: "Items que valen <strong>poco platino</strong> pero dan <strong>muchos ducados</strong>. Cómpralos barato para quemarlos."
    },
    loading: "Cargando datos del mercado...",
    table: {
      item: "Item",
      price: "Precio (Plat)",
      ducats: "Ducados",
      ratio: "Ratio (Duc/Plat)",
      action: "Acción",
      viewMarket: "Ver Mercado"
    },
    investment: {
      title: "🏛️ Oportunidades de Inversión",
      desc: "Items que pronto entrarán a la Bóveda (Vault). Su precio subirá cuando dejen de caer.",
      loading: "Analizando estado de la Bóveda...",
      badge: "PRONTO EN VAULT",
      action: "Comprar / Farmear",
      empty: "No hay items marcados como 'Próximos a Vault' en este momento."
    },
    modal: {
      loading: "Cargando datos completos...",
      components: "Componentes del Set",
      stats: {
        volume: "Volumen (48h)",
        min: "Mínimo",
        max: "Máximo",
        avg: "Promedio"
      },
      chartTitle: "Tendencia de Precios y Volumen (90 días)",
      sellers: "Vendedores",
      buyers: "Compradores",
      ai: {
        analyze: "🧠 Análisis IA",
        analyzing: "🔄 Analizando..."
      },
      viewMarket: "Ver en Warframe.market ↗",
      errorAnalysis: "Error al analizar el item.",
      chart: {
        avgPrice: "Precio Promedio",
        plat: "Platino",
        volume: "Volumen",
        maxRank: "Rango Máximo",
        intact: "Intacta"
      }
    }
  }
}
