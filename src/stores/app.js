import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getApiBase } from '../config'

export const useAppStore = defineStore('app', () => {
  const userId = ref(localStorage.getItem('pea_user_id') || null)
  const username = ref(localStorage.getItem('pea_username') || '')
  
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
  
  // Modals
  const isSettingsOpen = ref(false)
  const isAiAdvisorOpen = ref(false)
  const isFiscalModalOpen = ref(false)
  const isSearchModalOpen = ref(false)
  const isCommandPaletteOpen = ref(false)
  const inspectedAsset = ref(null)

  // Discretion Mode
  const isDiscreteMode = ref(localStorage.getItem('pea_discrete_mode') === 'true')

  const toggleDiscreteMode = () => {
    isDiscreteMode.value = !isDiscreteMode.value
    localStorage.setItem('pea_discrete_mode', isDiscreteMode.value)
  }

  const formatCurrency = (val) => {
    if (isDiscreteMode.value) return '*** €'
    return (val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
  }

  const cashAmount = computed(() => {
    return summary.value?.cash || 0
  })

  const setLoginData = (payload) => {
    userId.value = payload.userId
    username.value = payload.username
    fetchData()
  }

  const logout = () => {
    localStorage.removeItem('pea_user_id')
    localStorage.removeItem('pea_username')
    localStorage.removeItem('pea_access_token')
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
    try {
      const res = await fetch(`${getApiBase()}/api/dividends/metrics`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('pea_access_token')}` }
      })
      if (res.ok) {
        dividendMetrics.value = await res.json()
      }
    } catch (e) {
      console.error("Erreur fetch dividend metrics", e)
    }
  }

  const fetchData = async () => {
    if (!userId.value) return
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
        summary.value = await summaryRes.json()
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
    } catch (error) {
      console.error("Erreur lors de la récupération des données :", error)
    } finally {
      isLoading.value = false
    }
  }

  const refreshData = async () => {
    if (!userId.value) return
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
    } catch (error) {
      console.error("Erreur lors du rafraîchissement :", error)
    } finally {
      isRefreshing.value = false
    }
  }

  const isUploadingCsv = ref(false)
  const uploadCsv = async (file) => {
    if (!file || !userId.value) return { success: false, message: 'Fichier ou utilisateur non valide' }
    const apiBase = getApiBase()
    if (!apiBase) return { success: false, message: 'URL API non disponible' }

    isUploadingCsv.value = true
    const formData = new FormData()
    formData.append('file', file)

    try {
      const token = localStorage.getItem('pea_access_token')
      const res = await fetch(`${apiBase}/api/portfolio/upload?user_id=${userId.value}`, {
        method: 'POST',
        headers: token ? { Authorization: 'Bearer ' + token } : {},
        body: formData
      })

      if (res.ok) {
        await fetchData()
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
    positions,
    summary,
    history,
    weather,
    dividendMetrics,
    isLoading,
    isRefreshing,
    isAiLoading,
    isUploadingCsv,
    isSettingsOpen,
    isAiAdvisorOpen,
    isFiscalModalOpen,
    isSearchModalOpen,
    isCommandPaletteOpen,
    inspectedAsset,
    cashAmount,
    isDiscreteMode,
    toggleDiscreteMode,
    formatCurrency,
    setLoginData,
    logout,
    openStockInspector,
    fetchData,
    refreshData,
    uploadCsv
  }
})
