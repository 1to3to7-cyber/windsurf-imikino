import React, { useState, useEffect } from 'react'
import { Globe, Check } from 'lucide-react'
import { clsx } from 'clsx'

interface Language {
  code: string
  name: string
  flag: string
  rtl?: boolean
}

const languages: Language[] = [
  {
    code: 'rw',
    name: 'Kinyarwanda',
    flag: '🇷🇼',
    rtl: false
  },
  {
    code: 'en',
    name: 'English',
    flag: '🇬🇧',
    rtl: false
  },
  {
    code: 'fr',
    name: 'Français',
    flag: '🇫🇷',
    rtl: false
  },
  {
    code: 'sw',
    name: 'Kiswahili',
    flag: '🇰🇪',
    rtl: false
  }
]

interface LanguageSelectorProps {
  className?: string
  showLabel?: boolean
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  className,
  showLabel = true
}) => {
  const [currentLang, setCurrentLang] = useState('rw')
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    // Load saved language preference
    const saved = localStorage.getItem('imikino-language')
    if (saved && languages.find(lang => lang.code === saved)) {
      setCurrentLang(saved)
    }
  }, [])

  const handleLanguageChange = (langCode: string) => {
    setCurrentLang(langCode)
    localStorage.setItem('imikino-language', langCode)
    
    // Update document language and direction
    const lang = languages.find(l => l.code === langCode)
    if (lang) {
      document.documentElement.lang = langCode
      document.documentElement.dir = lang.rtl ? 'rtl' : 'ltr'
      
      // Trigger language change event for other components
      window.dispatchEvent(new CustomEvent('languagechange', {
        detail: { language: langCode, rtl: lang.rtl }
      }))
    }
    
    setIsOpen(false)
  }

  const currentLanguage = languages.find(lang => lang.code === currentLang)

  return (
    <div className={clsx('relative', className)}>
      {showLabel && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language / Icyongero
        </label>
      )}
      
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={clsx(
            'flex items-center space-x-2 px-4 py-2 bg-white border-2 border-gray-300 rounded-lg shadow-sm',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'hover:bg-gray-50 transition-colors duration-200'
          )}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
        >
          <span className="text-2xl">{currentLanguage?.flag}</span>
          <span className="font-medium">{currentLanguage?.name}</span>
          <Globe className="w-4 h-4 text-gray-400" />
        </button>
        
        {isOpen && (
          <div className="absolute z-50 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200">
            <div className="py-1">
              {languages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => handleLanguageChange(language.code)}
                  className={clsx(
                    'flex items-center w-full px-4 py-3 text-left hover:bg-gray-100',
                    'transition-colors duration-200',
                    currentLang === language.code && 'bg-primary-50 text-primary-600'
                  )}
                  role="option"
                  aria-selected={currentLang === language.code}
                >
                  <span className="text-xl mr-3">{language.flag}</span>
                  <div className="flex flex-col">
                    <span className="font-medium">{language.name}</span>
                    <span className="text-sm text-gray-500">{language.code.toUpperCase()}</span>
                  </div>
                  {currentLang === language.code && (
                    <Check className="w-4 h-4 text-primary-600 ml-auto" />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Hook for internationalization
export const useTranslation = () => {
  const [currentLang, setCurrentLang] = useState('rw')
  const [translations, setTranslations] = useState<Record<string, Record<string, string>>>({})

  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const response = await fetch(`/api/translations/${currentLang}.json`)
        const data = await response.json()
        setTranslations(data)
      } catch (error) {
        console.error('Failed to load translations:', error)
        // Fallback to basic translations
        setTranslations(getFallbackTranslations(currentLang))
      }
    }

    loadTranslations()
  }, [currentLang])

  const t = (key: string, fallback?: string) => {
    return translations[key] || fallback || key
  }

  const changeLanguage = (langCode: string) => {
    setCurrentLang(langCode)
    localStorage.setItem('imikino-language', langCode)
    document.documentElement.lang = langCode
    
    const lang = languages.find(l => l.code === langCode)
    if (lang) {
      document.documentElement.dir = lang.rtl ? 'rtl' : 'ltr'
    }
  }

  return { t, currentLang, changeLanguage, languages }
}

// Fallback translations for critical keys
const getFallbackTranslations = (lang: string): Record<string, string> => {
  const fallbacks: Record<string, Record<string, string>> = {
    rw: {
      welcome: 'Murakaza neza',
      login: 'Injira',
      register: 'Iyandikishe',
      profile: 'Irangamimerere',
      courses: 'Amahugurwa',
      tasks: 'Gahunda',
      posts: 'Inyandiko',
      logout: 'Sohoka',
      loading: 'Irimo...',
      error: 'Ikosa',
      retry: 'Ongera ugerageho',
      save: 'Bika',
      cancel: 'Kuraho'
    },
    en: {
      welcome: 'Welcome',
      login: 'Login',
      register: 'Register',
      profile: 'Profile',
      courses: 'Courses',
      tasks: 'Tasks',
      posts: 'Posts',
      logout: 'Logout',
      loading: 'Loading...',
      error: 'Error',
      retry: 'Retry',
      save: 'Save',
      cancel: 'Cancel'
    },
    fr: {
      welcome: 'Bienvenue',
      login: 'Connexion',
      register: "S'inscrire",
      profile: 'Profil',
      courses: 'Cours',
      tasks: 'Tâches',
      posts: 'Publications',
      logout: 'Déconnexion',
      loading: 'Chargement...',
      error: 'Erreur',
      retry: 'Réessayer',
      save: 'Enregistrer',
      cancel: 'Annuler'
    },
    sw: {
      welcome: 'Karibu',
      login: 'Ingia',
      register: 'Jisajili',
      profile: 'Wasifu',
      courses: 'Kozi',
      tasks: 'Kazi',
      posts: 'Chapisho',
      logout: 'Toka',
      loading: 'Inapakia...',
      error: 'Kosa',
      retry: 'Jaribu tena',
      save: 'Hifadhi',
      cancel: 'Ghairi'
    }
  }

  return fallbacks[lang] || fallbacks.en
}

// Number formatting for different locales
export const formatNumber = (num: number, lang: string = 'rw'): string => {
  const formatter = new Intl.NumberFormat(lang === 'rw' ? 'rw-RW' : lang)
  return formatter.format(num)
}

// Date formatting for different locales
export const formatDate = (date: Date, lang: string = 'rw'): string => {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }
  
  return new Intl.DateTimeFormat(lang === 'rw' ? 'rw-RW' : lang, options).format(date)
}

// Currency formatting for Rwanda
export const formatCurrency = (amount: number, lang: string = 'rw'): string => {
  return new Intl.NumberFormat(lang === 'rw' ? 'rw-RW' : lang, {
    style: 'currency',
    currency: 'RWF'
  }).format(amount)
}
