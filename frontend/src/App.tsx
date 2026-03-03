import { useState, useEffect, useCallback } from 'react';
import './index.css';
import Header from './components/Header';
import ImageUpload from './components/ImageUpload';
import AnalysisResults from './components/AnalysisResults';
import ScheduleCalendar from './components/ScheduleCalendar';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import { useApi } from './hooks/useApi';
import type { AnalysisResult, Alert, Patient, User, SignupData, CalendarEvent } from './types';

function App() {
  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  // App state
  const [activeTab, setActiveTab] = useState('analyze');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [alerts, setAlerts] = useState<(Alert | CalendarEvent)[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date());

  const {
    loading,
    error,
    signup,
    login,
    sendOtp,
    verifyOtp,
    analyzeImage,
    getCalendar,
    generateCalendar,
    addCalendarEvent,
    updateCalendarEvent,
    deleteCalendarEvent,
  } = useApi();

  // Check for saved session
  useEffect(() => {
    const savedPatient = localStorage.getItem('osteoai_patient');
    const savedUser = localStorage.getItem('osteoai_user');
    if (savedPatient) {
      try {
        setPatient(JSON.parse(savedPatient));
        if (savedUser) setUser(JSON.parse(savedUser));
        setIsAuthenticated(true);
      } catch {
        localStorage.removeItem('osteoai_patient');
        localStorage.removeItem('osteoai_user');
      }
    }
  }, []);

  // Load calendar when authenticated
  useEffect(() => {
    if (isAuthenticated && patient?.patientId) {
      loadCalendar();
    }
  }, [isAuthenticated, patient?.patientId]);

  const loadCalendar = async () => {
    if (!patient?.patientId) return;
    const result = await getCalendar(patient.patientId);
    if (result?.events) {
      setAlerts(result.events);
    }
  };

  // Handle signup
  const handleSignup = async (data: SignupData) => {
    const result = await signup(data);
    if (result?.patient) {
      setPatient(result.patient);
      setUser(result.user || null);
      setIsAuthenticated(true);
      localStorage.setItem('osteoai_patient', JSON.stringify(result.patient));
      if (result.user) localStorage.setItem('osteoai_user', JSON.stringify(result.user));
    }
  };

  // Handle password login
  const handleLogin = async (username: string, password: string) => {
    const result = await login({ username, password });
    if (result?.patient) {
      setPatient(result.patient);
      setUser(result.user || null);
      setIsAuthenticated(true);
      localStorage.setItem('osteoai_patient', JSON.stringify(result.patient));
      if (result.user) localStorage.setItem('osteoai_user', JSON.stringify(result.user));
    }
  };

  // Handle send OTP
  const handleSendOtp = async (whatsappNumber: string): Promise<string | null> => {
    const result = await sendOtp(whatsappNumber);
    return result?.otp || null;
  };

  // Handle verify OTP
  const handleVerifyOtp = async (whatsappNumber: string, otp: string) => {
    const result = await verifyOtp(whatsappNumber, otp);
    if (result?.patient) {
      setPatient(result.patient);
      setUser(result.user || null);
      setIsAuthenticated(true);
      localStorage.setItem('osteoai_patient', JSON.stringify(result.patient));
      if (result.user) localStorage.setItem('osteoai_user', JSON.stringify(result.user));
    }
  };

  // Handle logout
  const handleLogout = () => {
    setPatient(null);
    setUser(null);
    setIsAuthenticated(false);
    setAnalysisResult(null);
    setAlerts([]);
    setSelectedFile(null);
    setPreviewUrl(null);
    localStorage.removeItem('osteoai_patient');
    localStorage.removeItem('osteoai_user');
  };

  // Handle file selection
  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  // Handle file removal
  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setAnalysisResult(null);
  }, []);

  // Handle analysis
  const handleAnalyze = async () => {
    if (!selectedFile || !patient?.patientId) return;

    const result = await analyzeImage(selectedFile, patient.patientId);
    if (result) {
      setAnalysisResult(result);
      // Store alerts from recommendations
      if (result.alerts) {
        setAlerts(result.alerts);
      }
      // Update patient severity in local state
      setPatient(prev => prev ? { ...prev, severity: result.severity } : null);
      // Update localStorage
      if (patient) {
        localStorage.setItem('osteoai_patient', JSON.stringify({ ...patient, severity: result.severity }));
      }
    }
  };

  // Calendar handlers
  const handleAddEvent = async (event: Partial<CalendarEvent>) => {
    if (!patient?.patientId) return;
    const result = await addCalendarEvent(patient.patientId, event);
    if (result?.event) {
      setAlerts(prev => [...prev, result.event]);
    }
  };

  const handleUpdateEvent = async (eventId: string, event: Partial<CalendarEvent>) => {
    if (!patient?.patientId) return;
    await updateCalendarEvent(patient.patientId, eventId, event);
    // Reload calendar to get updated data
    await loadCalendar();
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!patient?.patientId) return;
    await deleteCalendarEvent(patient.patientId, eventId);
    setAlerts(prev => prev.filter(a => {
      const calEvent = a as CalendarEvent;
      return calEvent.eventId !== eventId;
    }));
  };

  const handleRegenerateCalendar = async () => {
    if (!patient?.patientId) return;
    const result = await generateCalendar(patient.patientId);
    if (result?.events) {
      setAlerts(result.events);
    }
  };

  // Show auth screens if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="app">
        <div className="bg-gradient" />

        {authMode === 'login' ? (
          <LoginForm
            onLogin={handleLogin}
            onSendOtp={handleSendOtp}
            onVerifyOtp={handleVerifyOtp}
            onSwitchToSignup={() => setAuthMode('signup')}
            loading={loading}
            error={error}
          />
        ) : (
          <SignupForm
            onSignup={handleSignup}
            onSwitchToLogin={() => setAuthMode('login')}
            loading={loading}
            error={error}
          />
        )}
      </div>
    );
  }

  return (
    <div className="app">
      <div className="bg-gradient" />

      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="main">
        {/* Patient Info Bar */}
        <div className="patient-info">
          <div className="patient-avatar">
            {user?.username?.charAt(0).toUpperCase() || 'P'}
          </div>
          <div className="patient-details">
            <div className="patient-name">{user?.username || 'Patient'}</div>
            <div className="patient-id">ID: {patient?.patientId}</div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>

        {activeTab === 'analyze' && (
          <>
            <div className="hero">
              <h1 className="hero-title">
                <span className="gradient-text">AI-Powered</span><br />
                Osteoarthritis Detection
              </h1>
              <p className="hero-subtitle">
                Upload a knee X-ray for instant severity analysis with personalized recommendations based on your age and medical history
              </p>
            </div>

            <div className="upload-section">
              <ImageUpload
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                onRemove={handleRemoveFile}
              />

              <button
                className={`btn btn-primary ${loading ? 'loading' : ''}`}
                onClick={handleAnalyze}
                disabled={!selectedFile || loading}
              >
                <span className="btn-text">
                  {loading ? 'Analyzing...' : 'Analyze X-ray'}
                </span>
                <div className="btn-loader" />
              </button>

              {error && (
                <div className="disclaimer" style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.3)', color: '#ef4444' }}>
                  ⚠️ {error}. Please make sure the server is running.
                </div>
              )}
            </div>

            {analysisResult && (
              <AnalysisResults
                result={analysisResult}
                onAddSuggestedAlerts={() => setActiveTab('calendar')}
              />
            )}
          </>
        )}

        {activeTab === 'calendar' && (
          <>
            <div className="hero" style={{ marginBottom: '2rem' }}>
              <h1 className="hero-title">
                <span className="gradient-text">Health</span> Schedule
              </h1>
              <p className="hero-subtitle">
                Your personalized health reminders based on your age, medical history, and diagnosis
              </p>
            </div>

            <div className="results-card">
              <ScheduleCalendar
                alerts={alerts}
                selectedDate={selectedDate}
                onDateSelect={setSelectedDate}
                onAddEvent={handleAddEvent}
                onUpdateEvent={handleUpdateEvent}
                onDeleteEvent={handleDeleteEvent}
                onRegenerateCalendar={handleRegenerateCalendar}
                loading={loading}
              />
            </div>
          </>
        )}

        {activeTab === 'about' && (
          <div className="results-card">
            <h2 className="result-title" style={{ marginBottom: '1.5rem' }}>About OsteoAI</h2>
            <div className="result-item">
              <p style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                OsteoAI is an AI-powered tool for analyzing knee X-rays to detect osteoarthritis severity levels.
                Using deep learning models combined with Ollama LLM, it provides instant analysis along with personalized recommendations
                tailored to your age and medical history.
              </p>

              <h3 className="item-title" style={{ marginTop: '1.5rem', marginBottom: '1rem' }}>
                <span className="item-icon">🔬</span> Features
              </h3>
              <ul className="recommendation-items">
                <li>Deep learning-based X-ray analysis</li>
                <li>5-level severity classification (Normal to Severe)</li>
                <li>AI-generated diet recommendations via Ollama</li>
                <li>Personalized exercise plans based on age & history</li>
                <li>Editable health calendar with AI suggestions</li>
                <li>Custom event creation and management</li>
              </ul>

              <h3 className="item-title" style={{ marginTop: '1.5rem', marginBottom: '1rem' }}>
                <span className="item-icon">👤</span> Your Profile
              </h3>
              <ul className="recommendation-items">
                <li>Patient ID: {patient?.patientId}</li>
                <li>Username: {user?.username}</li>
                <li>Age: {patient?.age} years</li>
                <li>WhatsApp: {patient?.whatsappNumber}</li>
                {patient?.severity && <li>Last Diagnosis: {patient.severity}</li>}
                {patient?.pastHistory && <li>Medical History: {patient.pastHistory}</li>}
              </ul>
            </div>

            <div className="disclaimer">
              ⚠️ This tool is for educational purposes only. Always consult with healthcare professionals for medical advice.
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>⚠️ This tool is for educational purposes only. Consult a healthcare professional for medical advice.</p>
      </footer>
    </div>
  );
}

export default App;
