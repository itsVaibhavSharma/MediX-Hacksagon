// frontend/src/components/Disease/ImageDetection.jsx
import React, { useState, useRef } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { api } from '../../services/api'
import { 
  Upload, 
  Camera, 
  X, 
  AlertCircle, 
  CheckCircle, 
  Brain,
  FileImage,
  Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'

const ImageDetection = () => {
  const { user } = useAuth()
  const [selectedModel, setSelectedModel] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [symptoms, setSymptoms] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [availableModels, setAvailableModels] = useState({})
  const fileInputRef = useRef(null)

  React.useEffect(() => {
    fetchAvailableModels()
  }, [])

  const fetchAvailableModels = async () => {
    try {
      const response = await api.get('/disease/models')
      setAvailableModels(response.data.model_descriptions)
    } catch (error) {
      console.error('Error fetching models:', error)
      toast.error('Failed to load available models')
    }
  }

  const handleImageSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('Image size should be less than 10MB')
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target.result)
        setImagePreview(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDetection = async () => {
    if (!selectedModel) {
      toast.error('Please select a disease type')
      return
    }

    if (!selectedImage) {
      toast.error('Please upload an image')
      return
    }

    setLoading(true)
    setResults(null)

    try {
      const response = await api.post('/disease/detect', {
        disease_type: selectedModel,
        image_base64: selectedImage,
        symptoms: symptoms.trim() || null
      })

      setResults(response.data)
      toast.success('Analysis completed successfully!')
    } catch (error) {
      console.error('Detection error:', error)
      toast.error(error.response?.data?.detail || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setSymptoms('')
    setResults(null)
    setSelectedModel('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI Disease Detection</h1>
        <p className="mt-2 text-gray-600">
          Upload medical images for AI-powered analysis and diagnosis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-6">
          {/* Model Selection */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Select Disease Type</h2>
            <div className="space-y-3">
              {Object.entries(availableModels).map(([key, description]) => (
                <label key={key} className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="model"
                    value={key}
                    checked={selectedModel === key}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <div>
                    <div className="text-sm font-medium text-gray-900 capitalize">
                      {key.replace('_', ' ')} Detection
                    </div>
                    <div className="text-sm text-gray-500">{description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Image Upload */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload Medical Image</h2>
            
            {!imagePreview ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
              >
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-600">
                  Click to upload or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  PNG, JPG, JPEG up to 10MB
                </p>
              </div>
            ) : (
              <div className="relative">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full h-64 object-cover rounded-lg"
                />
                <button
                  onClick={() => {
                    setSelectedImage(null)
                    setImagePreview(null)
                  }}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageSelect}
              className="hidden"
            />
          </div>

          {/* Optional Symptoms */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Additional Symptoms (Optional)
            </h2>
            <textarea
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Describe any symptoms you're experiencing... (This will help improve the AI analysis)"
              className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <p className="mt-2 text-xs text-gray-500">
              Adding symptoms helps our AI provide more accurate diagnosis
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleDetection}
              disabled={loading || !selectedModel || !selectedImage}
              className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Brain className="h-5 w-5" />
                  <span>Analyze Image</span>
                </>
              )}
            </button>
            
            <button
              onClick={resetForm}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {results ? (
            <>
              {/* AI Predictions */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center space-x-2 mb-4">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <h2 className="text-lg font-medium text-gray-900">AI Analysis Results</h2>
                </div>

                <div className="space-y-3">
                  {results.predictions.map((prediction, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        index === 0 
                          ? 'border-blue-200 bg-blue-50' 
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-900">
                          {prediction.disease}
                        </span>
                        <span className={`text-sm font-medium ${
                          prediction.confidence > 0.7 
                            ? 'text-green-600' 
                            : prediction.confidence > 0.4 
                            ? 'text-yellow-600' 
                            : 'text-red-600'
                        }`}>
                          {Math.round(prediction.confidence * 100)}%
                        </span>
                      </div>
                      <div className="mt-1 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            prediction.confidence > 0.7 
                              ? 'bg-green-500' 
                              : prediction.confidence > 0.4 
                              ? 'bg-yellow-500' 
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${prediction.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Final Diagnosis */}
              {results.final_diagnosis && (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <div className="flex items-center space-x-2 mb-4">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <h2 className="text-lg font-medium text-gray-900">AI Diagnosis</h2>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 font-medium">
                      Most Likely: {results.final_diagnosis}
                    </p>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {results.recommendations && (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <div className="flex items-center space-x-2 mb-4">
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                    <h2 className="text-lg font-medium text-gray-900">Recommendations</h2>
                  </div>
                  <div className="prose prose-sm max-w-none text-gray-700">
                    {results.recommendations.split('\n').map((line, index) => (
                      <p key={index} className="mb-2">{line}</p>
                    ))}
                  </div>
                </div>
              )}

              {/* Follow-up Questions */}
              {results.gemini_analysis && (
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">Follow-up Questions</h2>
                  <div className="prose prose-sm max-w-none text-gray-700">
                    {results.gemini_analysis.split('\n').map((line, index) => (
                      <p key={index} className="mb-2">{line}</p>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Next Steps</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => window.open('/chat', '_blank')}
                    className="flex items-center justify-center space-x-2 bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700"
                  >
                    <Brain className="h-5 w-5" />
                    <span>Continue Chat</span>
                  </button>
                  
                  <button
                    onClick={() => window.open('/book-appointment', '_blank')}
                    className="flex items-center justify-center space-x-2 bg-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-purple-700"
                  >
                    <Camera className="h-5 w-5" />
                    <span>Book Appointment</span>
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
              <FileImage className="mx-auto h-16 w-16 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">Ready for Analysis</h3>
              <p className="mt-2 text-gray-500">
                Select a disease type and upload an image to get started
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ImageDetection;