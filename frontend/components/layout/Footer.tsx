import React from 'react'
import { Mail, Phone, MapPin, GraduationCap, Code, Heart } from 'lucide-react'
import { useTranslation } from '@/components/ui/LanguageSelector'

export const Footer: React.FC = () => {
  const { t } = useTranslation()

  const developerInfo = {
    name: "BIZIMANA Fils",
    school: "ECOLE TECHNIQUE DOKABGAYI",
    nationalId: "1200780105863055",
    phones: ["0783444370", "0795914094"],
    district: "Muhanga District",
    email: "1to3to7@gmail.com"
  }

  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Developer Information */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-lg mb-4 flex items-center">
              <Code className="w-5 h-5 mr-2" />
              {t('developer', 'Developer')}
            </h3>
            <div className="space-y-2">
              <p className="font-medium text-white">{developerInfo.name}</p>
              <div className="flex items-start space-x-2">
                <GraduationCap className="w-4 h-4 mt-1 flex-shrink-0" />
                <span className="text-sm">{developerInfo.school}</span>
              </div>
              <div className="flex items-start space-x-2">
                <MapPin className="w-4 h-4 mt-1 flex-shrink-0" />
                <span className="text-sm">{developerInfo.district}</span>
              </div>
              <p className="text-xs text-gray-400">
                {t('national_id', 'National ID')}: {developerInfo.nationalId}
              </p>
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-lg mb-4 flex items-center">
              <Mail className="w-5 h-5 mr-2" />
              {t('contact', 'Contact')}
            </h3>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-primary-400" />
                <a 
                  href={`mailto:${developerInfo.email}`}
                  className="text-primary-400 hover:text-primary-300 transition-colors"
                >
                  {developerInfo.email}
                </a>
              </div>
              {developerInfo.phones.map((phone, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Phone className="w-4 h-4 text-primary-400" />
                  <a 
                    href={`tel:${phone}`}
                    className="text-primary-400 hover:text-primary-300 transition-colors"
                  >
                    {phone}
                  </a>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Links */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-lg mb-4">
              {t('platform', 'Platform')}
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="/about" className="text-gray-300 hover:text-white transition-colors">
                  {t('about_us', 'About Us')}
                </a>
              </li>
              <li>
                <a href="/courses" className="text-gray-300 hover:text-white transition-colors">
                  {t('courses', 'Courses')}
                </a>
              </li>
              <li>
                <a href="/tasks" className="text-gray-300 hover:text-white transition-colors">
                  {t('tasks', 'Tasks')}
                </a>
              </li>
              <li>
                <a href="/community" className="text-gray-300 hover:text-white transition-colors">
                  {t('community', 'Community')}
                </a>
              </li>
            </ul>
          </div>

          {/* Legal & Support */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-lg mb-4">
              {t('legal_support', 'Legal & Support')}
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="/privacy" className="text-gray-300 hover:text-white transition-colors">
                  {t('privacy_policy', 'Privacy Policy')}
                </a>
              </li>
              <li>
                <a href="/terms" className="text-gray-300 hover:text-white transition-colors">
                  {t('terms_of_service', 'Terms of Service')}
                </a>
              </li>
              <li>
                <a href="/help" className="text-gray-300 hover:text-white transition-colors">
                  {t('help_center', 'Help Center')}
                </a>
              </li>
              <li>
                <a href="/admin" className="text-gray-300 hover:text-white transition-colors">
                  {t('admin_access', 'Admin Access')}
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-gray-400">
              <p>
                © {currentYear} Imikino. {t('all_rights_reserved', 'All rights reserved.')}.
              </p>
              <p className="mt-1">
                {t('developed_by', 'Developed with')}{' '}
                <Heart className="w-4 h-4 inline text-red-500 mx-1" />{' '}
                {t('in_rwanda', 'in Rwanda')} {t('by', 'by')} {developerInfo.name}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-400">
                <p>{t('powered_by', 'Powered by')}</p>
                <p className="font-medium text-white">{developerInfo.school}</p>
              </div>
              
              {/* Rwanda Flag */}
              <div className="w-8 h-6 bg-blue-600 relative overflow-hidden rounded">
                <div className="absolute top-0 left-0 right-0 h-2 bg-yellow-400"></div>
                <div className="absolute top-2 left-0 right-0 h-2 bg-green-600"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Developer Attribution */}
        <div className="bg-gray-800 rounded-lg p-4 mt-6">
          <div className="text-center text-sm">
            <p className="text-gray-300">
              <span className="font-medium text-white">{t('technical_lead', 'Technical Lead & Developer')}:</span>{' '}
              {developerInfo.name} | {developerInfo.school}
            </p>
            <p className="text-xs text-gray-400 mt-2">
              {t('developer_credential', 'National ID')}: {developerInfo.nationalId} |{' '}
              {t('location', 'Location')}: {developerInfo.district}
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
