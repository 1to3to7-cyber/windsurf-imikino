'use client'

import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { useTranslation } from '@/components/ui/LanguageSelector'
import { Mail, Phone, MessageSquare, Send, CheckCircle } from 'lucide-react'

export default function ContactPage() {
  const { t, currentLang } = useTranslation()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
    category: 'general'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [submissionId, setSubmissionId] = useState('')

  const categories = [
    { value: 'general', label: t('general_inquiry', 'General Inquiry') },
    { value: 'technical', label: t('technical_support', 'Technical Support') },
    { value: 'academic', label: t('academic_questions', 'Academic Questions') },
    { value: 'feedback', label: t('feedback_suggestions', 'Feedback & Suggestions') },
    { value: 'partnership', label: t('partnership_opportunities', 'Partnership Opportunities') },
    { value: 'report', label: t('report_issue', 'Report an Issue') }
  ]

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      const response = await fetch('/api/contact/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        const data = await response.json()
        setSubmitStatus('success')
        setSubmissionId(data.submission_id)
        setFormData({
          name: '',
          email: '',
          phone: '',
          subject: '',
          message: '',
          category: 'general'
        })
      } else {
        setSubmitStatus('error')
      }
    } catch (error) {
      console.error('Contact form error:', error)
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t('contact_us', 'Contact Us')}
          </h1>
          <p className="text-gray-600 text-lg">
            {t('contact_description', 'Get in touch with the Imikino team. We\'ll respond within 24 hours.')}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Contact Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <div className="flex items-center space-x-3 mb-6">
                <Mail className="w-6 h-6 text-primary-600" />
                <h2 className="text-xl font-semibold text-gray-900">
                  {t('send_message', 'Send us a message')}
                </h2>
              </div>

              {submitStatus === 'success' && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <div>
                      <h3 className="font-semibold text-green-800">
                        {t('message_sent', 'Message Sent Successfully!')}
                      </h3>
                      <p className="text-green-700 text-sm">
                        {t('message_sent_desc', 'Your message has been sent to our team. We\'ll respond within 24 hours.')}
                      </p>
                      {submissionId && (
                        <p className="text-green-600 text-xs mt-2">
                          {t('reference_id', 'Reference ID')}: {submissionId}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Input
                    label={t('full_name', 'Full Name')}
                    value={formData.name}
                    onChange={(value) => handleInputChange('name', value)}
                    placeholder={t('name_placeholder', 'Enter your full name')}
                    required
                    leftIcon={<Mail className="w-4 h-4" />}
                  />

                  <Input
                    label={t('email_address', 'Email Address')}
                    type="email"
                    value={formData.email}
                    onChange={(value) => handleInputChange('email', value)}
                    placeholder={t('email_placeholder', 'your.email@example.com')}
                    required
                    leftIcon={<Mail className="w-4 h-4" />}
                  />
                </div>

                <Input
                  label={t('phone_number', 'Phone Number (Optional)')}
                  type="tel"
                  value={formData.phone}
                  onChange={(value) => handleInputChange('phone', value)}
                  placeholder={t('phone_placeholder', '+250 7xx xxx xxx')}
                  leftIcon={<Phone className="w-4 h-4" />}
                />

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    {t('category', 'Category')}
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  >
                    {categories.map(category => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>

                <Input
                  label={t('subject', 'Subject')}
                  value={formData.subject}
                  onChange={(value) => handleInputChange('subject', value)}
                  placeholder={t('subject_placeholder', 'What is this regarding?')}
                  required
                  leftIcon={<MessageSquare className="w-4 h-4" />}
                />

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    {t('message', 'Message')}
                  </label>
                  <textarea
                    value={formData.message}
                    onChange={(e) => handleInputChange('message', e.target.value)}
                    placeholder={t('message_placeholder', 'Tell us more about your inquiry...')}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center space-x-2"
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <LoadingSpinner size="sm" />
                      <span>{t('sending', 'Sending...')}</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>{t('send_message', 'Send Message')}</span>
                    </>
                  )}
                </Button>
              </form>

              {submitStatus === 'error' && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h3 className="font-semibold text-red-800">
                    {t('error_sending', 'Error Sending Message')}
                  </h3>
                  <p className="text-red-700 text-sm">
                    {t('try_again', 'Please try again or contact us directly at 1to3to7@gmail.com')}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Contact Information */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {t('contact_info', 'Contact Information')}
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Mail className="w-5 h-5 text-primary-600 mt-1" />
                  <div>
                    <h4 className="font-medium text-gray-900">Email</h4>
                    <p className="text-gray-600">1to3to7@gmail.com</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Phone className="w-5 h-5 text-primary-600 mt-1" />
                  <div>
                    <h4 className="font-medium text-gray-900">Phone</h4>
                    <p className="text-gray-600">0783444370 / 0795914094</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Mail className="w-5 h-5 text-primary-600 mt-1" />
                  <div>
                    <h4 className="font-medium text-gray-900">Response Time</h4>
                    <p className="text-gray-600">Within 24 hours</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Mail className="w-5 h-5 text-primary-600 mt-1" />
                  <div>
                    <h4 className="font-medium text-gray-900">Languages</h4>
                    <p className="text-gray-600">Kinyarwanda, English, French, Kiswahili</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-medium text-blue-800 mb-2">
                  {t('quick_response', 'Quick Response')}
                </h4>
                <p className="text-blue-700 text-sm">
                  {t('quick_response_desc', 'For urgent matters, please call us directly at +250 783444370')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
