// src/components/HomePage.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, 
  Brain, 
  Heart, 
  Shield, 
  Users, 
  Zap,
  Camera,
  MessageCircle,
  Calendar,
  ChevronRight,
  CheckCircle,
  Star,
  Award,
  Globe,
  Stethoscope
} from 'lucide-react';

const HomePage = () => {
  const [currentFeature, setCurrentFeature] = useState(0);

  useEffect(() => {
    // Auto-rotate features
    const timer = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % 3);
    }, 4000);

    return () => clearInterval(timer);
  }, []);

  const features = [
    {
      icon: Camera,
      title: "AI Image Analysis",
      description: "Upload medical images for instant AI-powered diagnosis across 6 specialized models",
      color: "from-blue-500 to-blue-600",
      image: "🔬"
    },
    {
      icon: MessageCircle,
      title: "Smart Symptom Chat",
      description: "Discuss your symptoms with our advanced AI assistant for personalized medical guidance",
      color: "from-green-500 to-green-600",
      image: "💬"
    },
    {
      icon: Calendar,
      title: "Doctor Consultations",
      description: "Book appointments with qualified doctors and attend video consultations seamlessly",
      color: "from-purple-500 to-purple-600",
      image: "👨‍⚕️"
    }
  ];

  const aiModels = [
    { name: "Skin Disease", icon: "🧴", accuracy: "92%", conditions: "22 conditions" },
    { name: "Eye Disease", icon: "👁️", accuracy: "89%", conditions: "5 conditions" },
    { name: "Bone Fracture", icon: "🦴", accuracy: "95%", conditions: "Binary detection" },
    { name: "Chest X-Ray", icon: "🫁", accuracy: "91%", conditions: "14 conditions" },
    { name: "Nail Disease", icon: "💅", accuracy: "96%", conditions: "6 conditions" },
    { name: "Oral Health", icon: "🦷", accuracy: "90%", conditions: "6 conditions" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="text-white space-y-8">
              <div className="space-y-4">
                <div className="flex items-center space-x-2 text-blue-200">
                  <Stethoscope className="h-6 w-6" />
                  <span className="text-sm font-medium">AI-Powered Healthcare</span>
                </div>
                <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                  Welcome to
                  <span className="block bg-gradient-to-r from-blue-200 to-white bg-clip-text text-transparent">
                    MediX Platform
                  </span>
                </h1>
                <p className="text-xl text-blue-100 leading-relaxed">
                  Revolutionary AI-powered medical diagnosis and consultation platform. 
                  Get instant medical insights with 6 specialized AI models and connect 
                  with qualified doctors worldwide.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  to="/login"
                  className="inline-flex items-center justify-center px-8 py-4 border-2 border-white text-white rounded-xl font-semibold hover:bg-white hover:text-blue-600 transition-all duration-300"
                >
                  Sign In
                </Link>
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-3 hover:rotate-0 transition-all duration-500">
                <div className="space-y-6">
                  <div className="flex items-center space-x-3">
                    <div className="bg-blue-100 p-3 rounded-full">
                      <Brain className="h-6 w-6 text-blue-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900">AI Diagnosis</h3>
                  </div>
                  
                  <div className="space-y-4">
                    {features.map((feature, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg transition-all duration-300 ${
                          currentFeature === index
                            ? 'bg-gradient-to-r ' + feature.color + ' text-white scale-105'
                            : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{feature.image}</span>
                          <div>
                            <h4 className="font-medium">{feature.title}</h4>
                            <p className={`text-sm ${currentFeature === index ? 'text-white' : 'text-gray-600'}`}>
                              {feature.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold text-gray-900">
              Cutting-Edge AI Medical Technology
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform combines advanced machine learning with medical expertise 
              to provide accurate, instant medical insights across multiple specialties.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {aiModels.map((model, index) => (
              <div key={index} className="bg-gradient-to-br from-white to-gray-50 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-4xl">{model.icon}</span>
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                      {model.accuracy}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{model.name}</h3>
                    <p className="text-gray-600">{model.conditions}</p>
                  </div>
                  <div className="pt-2">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-1000"
                        style={{ width: model.accuracy }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold text-gray-900">How MediX Works</h2>
            <p className="text-xl text-gray-600">Simple, fast, and accurate medical assistance in three steps</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Upload & Analyze",
                description: "Upload your medical images or describe symptoms to our AI system",
                icon: Camera,
                color: "bg-blue-500"
              },
              {
                step: "02", 
                title: "AI Processing",
                description: "Our specialized AI models analyze your data using advanced machine learning",
                icon: Brain,
                color: "bg-green-500"
              },
              {
                step: "03",
                title: "Get Results",
                description: "Receive instant diagnosis with confidence scores and doctor recommendations",
                icon: CheckCircle,
                color: "bg-purple-500"
              }
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
                  <div className="space-y-6">
                    <div className="flex items-center space-x-4">
                      <div className={`${item.color} text-white p-3 rounded-full`}>
                        <item.icon className="h-6 w-6" />
                      </div>
                      <span className="text-3xl font-bold text-gray-300">{item.step}</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{item.title}</h3>
                      <p className="text-gray-600">{item.description}</p>
                    </div>
                  </div>
                </div>
                {index < 2 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ChevronRight className="h-8 w-8 text-gray-300" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <div className="space-y-8">
            <div className="space-y-4">
              <h2 className="text-4xl font-bold text-white">
                Ready to Experience the Future of Healthcare?
              </h2>
              <p className="text-xl text-blue-100">
                Join thousands of users who trust MediX for their medical needs
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;