import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getApiBase } from '../config'

const DEMO_POSITIONS = [
  {
    name: 'Amundi MSCI World UCITS ETF (CW8)',
    ticker: 'CW8.PA',
    isin: 'LU1681043599',
    quantity: 28,
    pru: 445.20,
    current_price: 538.60,
    intraday_pct: 0.64,
    variation_pct: 20.98,
    sector: 'ETF & Indice',
    asset_type: 'ETF'
  },
  {
    name: 'Air Liquide',
    ticker: 'AI.PA',
    isin: 'FR0000120073',
    quantity: 45,
    pru: 148.50,
    current_price: 176.40,
    intraday_pct: 0.85,
    variation_pct: 18.79,
    sector: 'Industrie & Gaz',
    asset_type: 'Action'
  },
  {
    name: 'LVMH Moët Hennessy',
    ticker: 'MC.PA',
    isin: 'FR0000121014',
    quantity: 9,
    pru: 640.00,
    current_price: 718.50,
    intraday_pct: -0.35,
    variation_pct: 12.27,
    sector: 'Luxe',
    asset_type: 'Action'
  },
  {
    name: 'TotalEnergies',
    ticker: 'TTE.PA',
    isin: 'FR0000120271',
    quantity: 85,
    pru: 54.20,
    current_price: 63.80,
    intraday_pct: 1.15,
    variation_pct: 17.71,
    sector: 'Énergie',
    asset_type: 'Action'
  },
  {
    name: 'Schneider Electric',
    ticker: 'SU.PA',
    isin: 'FR0000121972',
    quantity: 22,
    pru: 182.00,
    current_price: 238.50,
    intraday_pct: 1.42,
    variation_pct: 31.04,
    sector: 'Technologie & Industrie',
    asset_type: 'Action'
  },
  {
    name: 'ASML Holding',
    ticker: 'ASML.AS',
    isin: 'NL0010273215',
    quantity: 5,
    pru: 690.00,
    current_price: 842.00,
    intraday_pct: 2.10,
    variation_pct: 22.03,
    sector: 'Semi-conducteurs / Tech',
    asset_type: 'Action'
  },
  {
    name: "L'Oréal",
    ticker: 'OR.PA',
    isin: 'FR0000120321',
    quantity: 8,
    pru: 395.00,
    current_price: 418.20,
    intraday_pct: 0.25,
    variation_pct: 5.87,
    sector: 'Luxe & Cosmétiques',
    asset_type: 'Action'
  },
  {
    name: 'BNP Paribas Easy S&P 500 (ESE)',
    ticker: 'ESE.PA',
    isin: 'FR0011550185',
    quantity: 160,
    pru: 21.40,
    current_price: 26.85,
    intraday_pct: 0.78,
    variation_pct: 25.47,
    sector: 'ETF & Indice',
    asset_type: 'ETF'
  }
]

function buildDemoHistory(totalVal, investedVal, cashVal) {
  const now = new Date()
  const points = []
  const steps = 12
  for (let i = steps; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 30 * 24 * 60 * 60 * 1000)
    const progress = (steps - i) / steps
    const wave = Math.sin(i * 0.9) * 650
    const stepInvested = Math.round(investedVal * (0.78 + 0.22 * progress))
    const stepTitres = Math.round(
      stepInvested + (totalVal - cashVal - investedVal) * Math.pow(progress, 1.15) + (i === 0 ? 0 : wave)
    )
    points.push({
      id: `demo-${i}`,
      snapshot_date: d.toISOString().slice(0, 10),
      date: d.toISOString().slice(0, 10),
      total_valeur: stepTitres + cashVal,
      valeur_titres: stepTitres,
      cash: cashVal,
      cout_investi: stepInvested,
      plus_value: stepTitres - stepInvested
    })
  }
  return points
}

export const useAppStore = defineStore('app', () => {
  const userId = ref(localStorage.getItem('pea_user_id') || null)
  const username = ref(localStorage.getItem('pea_username') || '')
  const isDemoMode = ref(localStorage.getItem('pea_demo_mode') === 'true')
  const peaOpenedAt = ref(localStorage.getItem('pea_opened_at') || '2020-03-15')

  // Data State
  const positions = ref([])
  const summary = ref(null)
  const history = ref([])
  const weather = ref(null)
  const dividendMetrics = ref(null)

  // UI State
  const isLoading = ref(false)
  const isRefreshing = ref(false)
  const isAiLoading = ref(false)
  const isAddPositionOpen = ref(false)
  const editingPosition = ref(null)

  // Toast Notification
  const toast = ref(null)
  let toastTimeout = null
  const showToast = (message, type = 'success') => {
    if (toastTimeout) clearTimeout(toastTimeout)
    toast.value = { message, type }
    toastTimeout = setTimeout(() => {
      toast.value = null
    }, 3500)
  }

  // Modals
  const isSettingsOpen = ref(false)
  const isAiAdvisorOpen = ref(false)
  const isFiscalModalOpen = ref(false)
  const isSearchModalOpen = ref(false)
  const isCommandPaletteOpen = ref(false)
  const inspectedAsset = ref(null)

  // Discretion Mode
  const isDiscreteMode = ref(localStorage.getItem('pea_discrete_mode') === 'true')
  const notifsRead = ref(false)

  const toggleDiscreteMode = () => {
    isDiscreteMode.value = !isDiscreteMode.value
    localStorage.setItem('pea_discrete_mode', isDiscreteMode.value)
  }

  // Cache the formatter to improve rendering performance
  const currencyFormatter = new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  const formatCurrency = (val) => {
    if (isDiscreteMode.value) return '••• €'
    return currencyFormatter.format(val || 0) + ' €'
  }

  const cashAmount = computed(() => {
    return summary.value?.cash || 0
  })

  // Helper: Check if a French stock is eligible for +10% loyalty bonus ("Nominatif Administré")
  const isNominatifEligible = (pos) => {
    if (!pos) return false
    const nameU = (pos.name || '').toUpperCase()
    const isinU = (pos.isin || '').toUpperCase()
    const tickerU = (pos.ticker || '').toUpperCase()
    return (
      nameU.includes('AIR LIQUIDE') ||
      isinU === 'FR0000120073' ||
      tickerU === 'AI.PA' ||
      nameU.includes('OREAL') ||
      nameU.includes('ORÉAL') ||
      isinU === 'FR0000120321' ||
      tickerU === 'OR.PA' ||
      nameU.includes('ENGIE') ||
      isinU === 'FR0010208488' ||
      tickerU === 'ENGI.PA' ||
      nameU.includes('SEB') ||
      isinU === 'FR0000121709' ||
      nameU.includes('SODEXO') ||
      isinU === 'FR0000121220'
    )
  }

  // Compute intraday portfolio variation
  const intradayVariation = computed(() => {
    if (!positions.value || !positions.value.length) {
      return { value: 0, pct: 0 }
    }
    let totalTitres = 0
    let dayGain = 0
    positions.value.forEach((p) => {
      const val = (p.quantity || 0) * (p.current_price || 0)
      totalTitres += val
      // Use intraday_pct if available, else estimate a realistic fraction from variation_pct
      const intraPct = p.intraday_pct !== undefined ? p.intraday_pct : (p.variation_pct ? Math.max(-2.5, Math.min(2.5, p.variation_pct * 0.035)) : 0.42)
      dayGain += val * (intraPct / 100)
    })
    const pct = totalTitres > 0 ? (dayGain / totalTitres) * 100 : 0
    return { value: dayGain, pct }
  })

  // Dynamic Smart Notifications based on real portfolio
  const notifications = computed(() => {
    const list = []
    if (!positions.value || positions.value.length === 0) {
      list.push({
        id: 'welcome',
        icon: '👋',
        color: 'bg-neonLime/20 text-neonLime',
        title: 'Bienvenue sur Capfolio PEA',
        desc: 'Importez votre CSV BoursoBank ou ajoutez une ligne manuellement pour démarrer.',
        time: 'À l’instant',
        route: '/portfolio'
      })
      return list
    }

    // 1. Check Nominatif Administré opportunities
    const nominatifList = positions.value.filter(isNominatifEligible)
    if (nominatifList.length > 0) {
      const names = nominatifList.map((p) => p.name).join(', ')
      list.push({
        id: 'nominatif',
        icon: '🎖️',
        color: 'bg-amberAcc/20 text-amberAcc',
        title: 'Prime de Fidélité +10% disponible',
        desc: `${names} : éligible au bonus +10% (dividendes & actions gratuites) au nominatif administré.`,
        time: 'Optimisation PEA',
        route: '/dividends'
      })
    }

    // 2. Check high concentration (> 25%)
    const totalV = summary.value?.total_value || 1
    const sortedByWeight = [...positions.value].sort(
      (a, b) => b.quantity * b.current_price - a.quantity * a.current_price
    )
    if (sortedByWeight[0]) {
      const top = sortedByWeight[0]
      const w = ((top.quantity * top.current_price) / totalV) * 100
      if (w > 22 &&top.sector !== 'ETF & Indice') {
        list.push({
          id: 'concentration',
          icon: '⚖️',
          color: 'bg-neonPurple/20 text-lavender',
          title: `Pondération élevée : ${top.name}`,
          desc: `Représente ${w.toFixed(1)}% de votre PEA. Pensez à vérifier votre équilibre.`,
          time: 'Gestion du risque',
          route: '/plan'
        })
      }
    }

    // 3. Dividend income notification
    if (dividendMetrics.value?.estimated_annual_income > 0) {
      list.push({
        id: 'div-income',
        icon: '💰',
        color: 'bg-neonLime/20 text-neonLime',
        title: `Rente annuelle estimée : ${Math.round(dividendMetrics.value.estimated_annual_income)} €`,
        desc: `Soit ~${Math.round(dividendMetrics.value.estimated_annual_income / 12)} €/mois réinvestis en franchise d'impôt.`,
        time: 'Projection Rente',
        route: '/dividends'
      })
    }

    // 4. Best performer highlight
    const best = [...positions.value].sort((a, b) => (b.variation_pct || 0) - (a.variation_pct || 0))[0]
    if (best && best.variation_pct > 10) {
      list.push({
        id: 'best-perf',
        icon: '🚀',
        color: 'bg-cyanAcc/20 text-cyanAcc',
        title: `Locomotive : ${best.name}`,
        desc: `Plus-value latente de +${best.variation_pct.toFixed(1)}% sur cette ligne.`,
        time: 'Performance',
        route: '/performance'
      })
    }

    return list
  })

  const unreadNotifCount = computed(() => (notifsRead.value ? 0 : notifications.value.length))
  const markAllNotificationsRead = () => {
    notifsRead.value = true
  }

  const computeTaxStatusFromDate = (openedDateStr, netInvested) => {
    const opened = new Date(openedDateStr || '2020-03-15')
    const maturity = new Date(opened)
    maturity.setFullYear(maturity.getFullYear() + 5)
    const now = new Date()
    const diffDays = Math.ceil((maturity.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    const isMature = diffDays <= 0
    return {
      opened_at: opened.toISOString().slice(0, 10),
      maturity_date: maturity.toISOString().slice(0, 10),
      days_to_maturity: Math.max(0, diffDays),
      is_mature: isMature,
      net_invested: round2(netInvested),
      legal_limit: 150000,
      capacity_left: round2(Math.max(0, 150000 - netInvested)),
      social_taxes_pct: 17.2
    }
  }

  const round2 = (n) => Math.round((Number(n) || 0) * 100) / 100

  const recalculateLocalSummary = (customCash = null) => {
    const cashVal = customCash !== null ? Number(customCash) : Number(summary.value?.cash ?? 2450)
    const valTitres = positions.value.reduce((acc, p) => acc + (p.quantity || 0) * (p.current_price || 0), 0)
    const totalInvested = positions.value.reduce((acc, p) => acc + (p.quantity || 0) * (p.pru || 0), 0)
    const totalValue = valTitres + cashVal
    const perfValue = valTitres - totalInvested
    const perfPct = totalInvested > 0 ? (perfValue / totalInvested) * 100 : 0

    summary.value = {
      total_value: round2(totalValue),
      total_invested: round2(totalInvested),
      global_performance_pct: round2(perfPct),
      global_performance_value: round2(perfValue),
      cash: round2(cashVal),
      last_updated: new Date().toISOString(),
      performance: {
        xirr: round2((perfPct / 100) * 0.42),
        net_invested: round2(totalInvested),
        total_deposits: round2(totalInvested + cashVal),
        total_withdrawals: 0
      },
      tax_status: computeTaxStatusFromDate(peaOpenedAt.value, totalInvested + cashVal)
    }

    // Also compute dividendMetrics locally if in demo mode or fallback
    const divYieldMap = {
      'TTE.PA': 4.95,
      'AI.PA': 1.95,
      'MC.PA': 1.85,
      'SU.PA': 1.55,
      'OR.PA': 1.60,
      'ASML.AS': 0.85,
      'CW8.PA': 0.0,
      'ESE.PA': 0.0
    }
    let totalDivIncome = 0
    const divPositions = []
    positions.value.forEach((p) => {
      const val = p.quantity * p.current_price
      const cost = p.quantity * p.pru
      const yld = divYieldMap[p.ticker] !== undefined ? divYieldMap[p.ticker] : (p.sector === 'ETF & Indice' ? 0 : 2.1)
      const income = val * (yld / 100)
      if (income > 0) {
        totalDivIncome += income
        divPositions.push({
          ticker: p.ticker,
          isin: p.isin,
          name: p.name,
          quantity: p.quantity,
          annual_income: round2(income),
          yield: round2(yld),
          yield_on_cost: cost > 0 ? round2((income / cost) * 100) : round2(yld),
          safety_score: isNominatifEligible(p) ? 92 : 84,
          is_nominatif: isNominatifEligible(p)
        })
      }
    })
    dividendMetrics.value = {
      estimated_annual_income: round2(totalDivIncome),
      average_yield: valTitres > 0 ? round2((totalDivIncome / valTitres) * 100) : 0,
      yield_on_cost: totalInvested > 0 ? round2((totalDivIncome / totalInvested) * 100) : 0,
      safety_score: 86,
      positions: divPositions,
      received_dividends: []
    }
  }

  const enterDemoMode = () => {
    isDemoMode.value = true
    userId.value = 'demo-investor'
    username.value = 'Investisseur Démo'
    localStorage.setItem('pea_demo_mode', 'true')
    localStorage.setItem('pea_user_id', 'demo-investor')
    localStorage.setItem('pea_username', 'Investisseur Démo')

    positions.value = JSON.parse(JSON.stringify(DEMO_POSITIONS))
    recalculateLocalSummary(2450)
    history.value = buildDemoHistory(
      summary.value.total_value,
      summary.value.total_invested,
      summary.value.cash
    )
    weather.value = {
      score: 0.38,
      emoji: '☀️',
      text: 'Momentum Haussier',
      details: {}
    }
    showToast('Mode Démo activé — Explorez librement toutes les fonctionnalités !', 'success')
  }

  const setPeaOpenedAt = (dateStr) => {
    if (!dateStr) return
    peaOpenedAt.value = dateStr
    localStorage.setItem('pea_opened_at', dateStr)
    if (summary.value) {
      summary.value.tax_status = computeTaxStatusFromDate(
        dateStr,
        summary.value.total_invested + (summary.value.cash || 0)
      )
    }
    showToast("Date d'ouverture du PEA mise à jour !", 'success')
  }

  const openAddPositionModal = (posToEdit = null) => {
    editingPosition.value = posToEdit ? { ...posToEdit } : null
    isAddPositionOpen.value = true
  }

  const upsertPosition = async (posPayload) => {
    const cleanPos = {
      name: (posPayload.name || '').trim(),
      ticker: (posPayload.ticker || posPayload.isin || '').trim().toUpperCase(),
      isin: (posPayload.isin || posPayload.ticker || '').trim().toUpperCase(),
      quantity: Number(posPayload.quantity) || 0,
      pru: Number(posPayload.pru) || 0,
      current_price: Number(posPayload.current_price || posPayload.pru) || 0,
      sector: posPayload.sector || 'Action',
      asset_type: posPayload.asset_type || (posPayload.sector === 'ETF & Indice' ? 'ETF' : 'Action')
    }
    cleanPos.variation_pct =
      cleanPos.pru > 0 ? round2(((cleanPos.current_price - cleanPos.pru) / cleanPos.pru) * 100) : 0

    const idx = positions.value.findIndex(
      (p) =>
        (p.ticker && p.ticker === cleanPos.ticker) ||
        (p.isin && p.isin === cleanPos.isin) ||
        p.name.toLowerCase() === cleanPos.name.toLowerCase()
    )
    if (idx !== -1) {
      positions.value[idx] = { ...positions.value[idx], ...cleanPos }
    } else {
      positions.value.unshift(cleanPos)
    }

    recalculateLocalSummary()
    history.value = buildDemoHistory(
      summary.value.total_value,
      summary.value.total_invested,
      summary.value.cash
    )

    // If connected to real backend (not demo), persist via API if available
    if (!isDemoMode.value && userId.value) {
      try {
        const apiBase = getApiBase()
        const token = localStorage.getItem('pea_access_token')
        await fetch(`${apiBase}/api/portfolio/position`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: 'Bearer ' + token } : {})
          },
          body: JSON.stringify(cleanPos)
        })
      } catch (e) {
        console.warn('Position saved locally (backend endpoint optional):', e)
      }
    }

    isAddPositionOpen.value = false
    showToast(`Ligne "${cleanPos.name}" enregistrée avec succès !`, 'success')
  }

  const removePosition = async (pos) => {
    if (!pos) return
    positions.value = positions.value.filter(
      (p) => p.ticker !== pos.ticker && p.name !== pos.name
    )
    recalculateLocalSummary()
    showToast(`Ligne "${pos.name}" retirée du portefeuille.`, 'info')
  }

  const setLoginData = (payload) => {
    isDemoMode.value = false
    localStorage.removeItem('pea_demo_mode')
    userId.value = payload.userId
    username.value = payload.username
    localStorage.setItem('pea_user_id', payload.userId)
    localStorage.setItem('pea_username', payload.username)
    fetchData()
  }

  const logout = () => {
    localStorage.removeItem('pea_user_id')
    localStorage.removeItem('pea_username')
    localStorage.removeItem('pea_access_token')
    localStorage.removeItem('pea_demo_mode')
    isDemoMode.value = false
    userId.value = null
    username.value = ''
    positions.value = []
    summary.value = null
    history.value = []
  }

  const openStockInspector = (stock) => {
    if (!stock) return
    inspectedAsset.value = stock
    isSearchModalOpen.value = true
  }

  const fetchDividendMetrics = async () => {
    if (isDemoMode.value) return
    try {
      const res = await fetch(`${getApiBase()}/api/dividends/metrics`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('pea_access_token')}` }
      })
      if (res.ok) {
        dividendMetrics.value = await res.json()
      }
    } catch (e) {
      console.error('Erreur fetch dividend metrics', e)
    }
  }

  const fetchWeather = async () => {
    if (isDemoMode.value) return
    try {
      const token = localStorage.getItem('pea_access_token')
      const res = await fetch(`${getApiBase()}/api/portfolio/weather`, {
        headers: token ? { Authorization: 'Bearer ' + token } : {}
      })
      if (res.ok) {
        weather.value = await res.json()
      }
    } catch (e) {
      // Non-blocking weather fetch
    }
  }

  const fetchData = async () => {
    if (!userId.value) return
    if (isDemoMode.value) {
      if (positions.value.length === 0) enterDemoMode()
      return
    }
    const apiBase = getApiBase()
    if (!apiBase) return

    isLoading.value = true
    try {
      const token = localStorage.getItem('pea_access_token')
      const headers = token ? { Authorization: 'Bearer ' + token } : {}

      const [summaryRes, positionsRes, historyRes] = await Promise.all([
        fetch(`${apiBase}/api/portfolio/summary?user_id=${userId.value}`, { headers }).catch(() => null),
        fetch(`${apiBase}/api/portfolio/positions?user_id=${userId.value}`, { headers }).catch(() => null),
        fetch(`${apiBase}/api/portfolio/history?user_id=${userId.value}`, { headers }).catch(() => null)
      ])

      if (summaryRes && summaryRes.ok) {
        const sumData = await summaryRes.json()
        // Ensure custom PEA opened_at date is respected if set by user
        if (localStorage.getItem('pea_opened_at') && sumData.tax_status) {
          sumData.tax_status = computeTaxStatusFromDate(
            peaOpenedAt.value,
            (sumData.total_invested || 0) + (sumData.cash || 0)
          )
        } else if (sumData.tax_status) {
          sumData.tax_status.social_taxes_pct = 17.2
        }
        summary.value = sumData
      }
      if (positionsRes && positionsRes.ok) {
        const posData = await positionsRes.json()
        positions.value = posData.positions || []
      }
      if (historyRes && historyRes.ok) {
        const histData = await historyRes.json()
        history.value = histData.history || []
      }

      await fetchDividendMetrics()
      fetchWeather()
    } catch (error) {
      console.error('Erreur lors de la récupération des données :', error)
    } finally {
      isLoading.value = false
    }
  }

  const refreshData = async () => {
    if (!userId.value) return
    if (isDemoMode.value) {
      isRefreshing.value = true
      setTimeout(() => {
        positions.value = positions.value.map((p) => {
          const delta = 1 + (Math.random() * 0.016 - 0.006)
          const newPrice = round2(p.current_price * delta)
          return {
            ...p,
            current_price: newPrice,
            variation_pct: round2(((newPrice - p.pru) / p.pru) * 100)
          }
        })
        recalculateLocalSummary()
        isRefreshing.value = false
        showToast('Cours actualisés en direct !', 'success')
      }, 650)
      return
    }

    const apiBase = getApiBase()
    if (!apiBase) return
    isRefreshing.value = true
    try {
      const token = localStorage.getItem('pea_access_token')
      await fetch(`${apiBase}/api/portfolio/refresh?user_id=${userId.value}`, {
        method: 'POST',
        headers: token ? { Authorization: 'Bearer ' + token } : {}
      })
      await fetchData()
      showToast('Cours et historique synchronisés avec Yahoo Finance !', 'success')
    } catch (error) {
      console.error('Erreur lors du rafraîchissement :', error)
      showToast('Erreur lors de la synchronisation des cours', 'error')
    } finally {
      isRefreshing.value = false
    }
  }

  const isUploadingCsv = ref(false)
  const uploadCsv = async (file) => {
    if (!file || !userId.value)
      return { success: false, message: 'Utilisateur non connecté ou fichier manquant' }
    const apiBase = getApiBase()

    isUploadingCsv.value = true
    const formData = new FormData()
    formData.append('file', file)

    try {
      const token = localStorage.getItem('pea_access_token')
      const url = `${apiBase}/api/portfolio/upload?user_id=${userId.value}`
      const res = await fetch(url, {
        method: 'POST',
        headers: token ? { Authorization: 'Bearer ' + token } : {},
        body: formData
      })

      if (res.ok) {
        isDemoMode.value = false
        localStorage.removeItem('pea_demo_mode')
        await fetchData()
        showToast('Portefeuille importé avec succès !', 'success')
        return { success: true, message: 'Portefeuille importé avec succès !' }
      } else {
        const err = await res.json().catch(() => ({}))
        const msg = err.detail || "Erreur lors de l'importation. Format CSV invalide."
        return { success: false, message: msg }
      }
    } catch (e) {
      return { success: false, message: "Erreur réseau lors de l'envoi du fichier" }
    } finally {
      isUploadingCsv.value = false
    }
  }

  return {
    userId,
    username,
    isDemoMode,
    peaOpenedAt,
    positions,
    summary,
    history,
    weather,
    dividendMetrics,
    intradayVariation,
    notifications,
    unreadNotifCount,
    markAllNotificationsRead,
    isNominatifEligible,
    isLoading,
    isRefreshing,
    isAiLoading,
    isUploadingCsv,
    isSettingsOpen,
    isAiAdvisorOpen,
    isFiscalModalOpen,
    isSearchModalOpen,
    isCommandPaletteOpen,
    isAddPositionOpen,
    editingPosition,
    inspectedAsset,
    toast,
    showToast,
    cashAmount,
    isDiscreteMode,
    toggleDiscreteMode,
    formatCurrency,
    setLoginData,
    enterDemoMode,
    setPeaOpenedAt,
    openAddPositionModal,
    upsertPosition,
    removePosition,
    recalculateLocalSummary,
    logout,
    openStockInspector,
    fetchData,
    refreshData,
    uploadCsv
  }
})
