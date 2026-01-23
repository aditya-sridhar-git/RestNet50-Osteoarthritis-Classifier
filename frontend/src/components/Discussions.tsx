import { useState, useEffect, useRef, useCallback } from 'react';
import { useApi } from '../hooks/useApi';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'ai';
    translation?: string;
}

interface DiscussionsProps {
    patientId: string;
    language: 'en' | 'kn';
}

type VoiceState = 'idle' | 'listening' | 'talking';

export default function Discussions({ patientId, language }: DiscussionsProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [voiceState, setVoiceState] = useState<VoiceState>('idle');
    const [audioLevels, setAudioLevels] = useState<number[]>(Array(12).fill(0.3));
    const { sendChatMessage, loading } = useApi();
    const chatEndRef = useRef<HTMLDivElement>(null);
    const recognitionRef = useRef<any>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const analyzerRef = useRef<AnalyserNode | null>(null);
    const animationRef = useRef<number | null>(null);
    const voicesLoadedRef = useRef<boolean>(false);

    // Load voices on mount
    useEffect(() => {
        const synth = window.speechSynthesis;

        const loadVoices = () => {
            const voices = synth.getVoices();
            if (voices.length > 0) {
                voicesLoadedRef.current = true;
            }
        };

        loadVoices();
        synth.addEventListener('voiceschanged', loadVoices);

        return () => {
            synth.removeEventListener('voiceschanged', loadVoices);
        };
    }, []);

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'kn-IN';

            recognition.onresult = async (event: any) => {
                const text = event.results[0][0].transcript;
                stopAudioVisualization();
                setVoiceState('idle');
                if (text) {
                    await handleSendMessage(text);
                }
            };

            recognition.onerror = () => {
                stopAudioVisualization();
                setVoiceState('idle');
            };

            recognition.onend = () => {
                if (voiceState === 'listening') {
                    stopAudioVisualization();
                    setVoiceState('idle');
                }
            };

            recognitionRef.current = recognition;
        }

        return () => {
            stopAudioVisualization();
        };
    }, []);

    // Scroll to bottom when messages change
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Audio visualization animation
    const startAudioVisualization = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioContextRef.current = new AudioContext();
            analyzerRef.current = audioContextRef.current.createAnalyser();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            source.connect(analyzerRef.current);
            analyzerRef.current.fftSize = 32;

            const bufferLength = analyzerRef.current.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);

            const updateLevels = () => {
                if (analyzerRef.current) {
                    analyzerRef.current.getByteFrequencyData(dataArray);
                    const newLevels = Array(12).fill(0).map((_, i) => {
                        const value = dataArray[i % bufferLength] / 255;
                        return 0.3 + value * 0.7;
                    });
                    setAudioLevels(newLevels);
                }
                animationRef.current = requestAnimationFrame(updateLevels);
            };
            updateLevels();
        } catch (err) {
            // Fallback to random animation if mic access fails
            const animateRandom = () => {
                setAudioLevels(prev => prev.map(() => 0.3 + Math.random() * 0.7));
                animationRef.current = requestAnimationFrame(animateRandom);
            };
            animateRandom();
        }
    };

    const stopAudioVisualization = () => {
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
            animationRef.current = null;
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
        setAudioLevels(Array(12).fill(0.3));
    };

    const speak = useCallback((text: string, lang: string) => {
        const synth = window.speechSynthesis;
        if (!synth) {
            console.error('[TTS] Speech synthesis not supported');
            return;
        }

        console.log('[TTS] Speaking text:', text.substring(0, 50) + '...');
        console.log('[TTS] Language:', lang);

        // Cancel any ongoing speech
        synth.cancel();

        // Function to actually speak
        const doSpeak = () => {
            const utterance = new SpeechSynthesisUtterance(text);

            // Get available voices
            const voices = synth.getVoices();
            console.log('[TTS] Available voices:', voices.length);

            // Try to find the best voice
            let selectedVoice: SpeechSynthesisVoice | undefined;

            if (lang === 'kn') {
                // Try Kannada first
                selectedVoice = voices.find(v => v.lang === 'kn-IN' || v.lang.startsWith('kn'));
                // Try Hindi as fallback (similar script)
                if (!selectedVoice) {
                    selectedVoice = voices.find(v => v.lang === 'hi-IN' || v.lang.startsWith('hi'));
                }
                // Try any Indian English
                if (!selectedVoice) {
                    selectedVoice = voices.find(v => v.lang === 'en-IN');
                }
            }

            // Default to any English voice
            if (!selectedVoice) {
                selectedVoice = voices.find(v => v.lang.startsWith('en'));
            }

            // Last resort - first available voice
            if (!selectedVoice && voices.length > 0) {
                selectedVoice = voices[0];
            }

            if (selectedVoice) {
                utterance.voice = selectedVoice;
                console.log('[TTS] Selected voice:', selectedVoice.name, selectedVoice.lang);
            }

            // Set language
            utterance.lang = lang === 'kn' ? 'kn-IN' : 'en-US';
            utterance.rate = 0.85;
            utterance.pitch = 1;
            utterance.volume = 1;

            utterance.onstart = () => {
                console.log('[TTS] Started speaking');
                setVoiceState('talking');
                // Animate while talking
                const animateTalking = () => {
                    if (synth.speaking) {
                        setAudioLevels(prev => prev.map(() => 0.4 + Math.random() * 0.6));
                        animationRef.current = requestAnimationFrame(animateTalking);
                    }
                };
                animateTalking();
            };

            utterance.onend = () => {
                console.log('[TTS] Finished speaking');
                stopAudioVisualization();
                setVoiceState('idle');
            };

            utterance.onerror = (e) => {
                console.error('[TTS] Speech error:', e.error);
                stopAudioVisualization();
                setVoiceState('idle');
            };

            synth.speak(utterance);
            console.log('[TTS] Speak command sent');
        };

        // Voices might not be loaded immediately
        const voices = synth.getVoices();
        if (voices.length > 0) {
            doSpeak();
        } else {
            // Wait for voices to load
            console.log('[TTS] Waiting for voices to load...');
            const handleVoicesChanged = () => {
                synth.removeEventListener('voiceschanged', handleVoicesChanged);
                doSpeak();
            };
            synth.addEventListener('voiceschanged', handleVoicesChanged);

            // Fallback timeout - try anyway after 500ms
            setTimeout(() => {
                synth.removeEventListener('voiceschanged', handleVoicesChanged);
                if (!synth.speaking) {
                    console.log('[TTS] Timeout - trying to speak anyway');
                    doSpeak();
                }
            }, 500);
        }
    }, []);

    const handleSendMessage = async (text: string) => {
        const userMsg: Message = {
            id: Date.now().toString(),
            text,
            sender: 'user'
        };
        setMessages(prev => [...prev, userMsg]);

        const aiResponse = await sendChatMessage(patientId, text);
        if (aiResponse) {
            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: aiResponse.response_kn,
                sender: 'ai',
                translation: aiResponse.response_en
            };
            setMessages(prev => [...prev, aiMsg]);

            // Speak the response in Kannada
            speak(aiResponse.response_kn, 'kn');
        }
    };

    const toggleListening = () => {
        if (voiceState === 'listening') {
            recognitionRef.current?.stop();
            stopAudioVisualization();
            setVoiceState('idle');
        } else if (voiceState === 'idle') {
            setVoiceState('listening');
            startAudioVisualization();
            recognitionRef.current?.start();
        }
    };

    // Generate circular segments for visualizer
    const generateSegments = () => {
        const segments = [];
        const numSegments = 12;
        const centerX = 100;
        const centerY = 100;
        const innerRadius = 50;
        const maxOuterRadius = 90;

        for (let i = 0; i < numSegments; i++) {
            const angle = (i * 360 / numSegments - 90) * (Math.PI / 180);
            const nextAngle = ((i + 1) * 360 / numSegments - 90) * (Math.PI / 180);
            const gap = 0.03;

            const level = audioLevels[i];
            const outerRadius = innerRadius + (maxOuterRadius - innerRadius) * level;

            const x1Inner = centerX + innerRadius * Math.cos(angle + gap);
            const y1Inner = centerY + innerRadius * Math.sin(angle + gap);
            const x2Inner = centerX + innerRadius * Math.cos(nextAngle - gap);
            const y2Inner = centerY + innerRadius * Math.sin(nextAngle - gap);
            const x1Outer = centerX + outerRadius * Math.cos(angle + gap);
            const y1Outer = centerY + outerRadius * Math.sin(angle + gap);
            const x2Outer = centerX + outerRadius * Math.cos(nextAngle - gap);
            const y2Outer = centerY + outerRadius * Math.sin(nextAngle - gap);

            const path = `M ${x1Inner} ${y1Inner} L ${x1Outer} ${y1Outer} A ${outerRadius} ${outerRadius} 0 0 1 ${x2Outer} ${y2Outer} L ${x2Inner} ${y2Inner} A ${innerRadius} ${innerRadius} 0 0 0 ${x1Inner} ${y1Inner}`;

            segments.push(
                <path
                    key={i}
                    d={path}
                    className={`visualizer-segment ${voiceState}`}
                    style={{
                        animationDelay: `${i * 0.05}s`,
                        opacity: 0.6 + level * 0.4
                    }}
                />
            );
        }
        return segments;
    };

    return (
        <div className="discussions-container-new">
            {/* Visualizer Section */}
            <div className="voice-visualizer-container">
                <div className="visualizer-wrapper">
                    <svg viewBox="0 0 200 200" className="circular-visualizer">
                        <defs>
                            <linearGradient id="segmentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#6366f1" />
                                <stop offset="50%" stopColor="#8b5cf6" />
                                <stop offset="100%" stopColor="#a855f7" />
                            </linearGradient>
                            <linearGradient id="listeningGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#10b981" />
                                <stop offset="100%" stopColor="#34d399" />
                            </linearGradient>
                            <linearGradient id="talkingGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#f59e0b" />
                                <stop offset="100%" stopColor="#fbbf24" />
                            </linearGradient>
                        </defs>
                        {generateSegments()}
                        {/* Center circle */}
                        <circle
                            cx="100"
                            cy="100"
                            r="45"
                            className={`visualizer-center ${voiceState}`}
                        />
                        {/* Center icon */}
                        <text
                            x="100"
                            y="108"
                            textAnchor="middle"
                            className="visualizer-icon"
                        >
                            {voiceState === 'idle' && '🎤'}
                            {voiceState === 'listening' && '🎧'}
                            {voiceState === 'talking' && '🔊'}
                        </text>
                    </svg>
                </div>

                {/* State Buttons */}
                <div className="voice-state-buttons">
                    <button
                        className={`state-btn ${voiceState === 'idle' ? 'active' : ''}`}
                        onClick={() => {
                            if (voiceState !== 'idle') {
                                window.speechSynthesis.cancel();
                                recognitionRef.current?.stop();
                                stopAudioVisualization();
                                setVoiceState('idle');
                            }
                        }}
                    >
                        {language === 'en' ? 'Idle' : 'ವಿಶ್ರಾಂತಿ'}
                    </button>
                    <button
                        className={`state-btn listening ${voiceState === 'listening' ? 'active' : ''}`}
                        onClick={toggleListening}
                        disabled={loading || voiceState === 'talking'}
                    >
                        {language === 'en' ? 'Listening' : 'ಆಲಿಸುತ್ತಿದೆ'}
                    </button>
                    <button
                        className={`state-btn talking ${voiceState === 'talking' ? 'active' : ''}`}
                        disabled
                    >
                        {language === 'en' ? 'Talking' : 'ಮಾತನಾಡುತ್ತಿದೆ'}
                    </button>
                </div>

                {/* Status Text */}
                <div className="voice-status-text">
                    {voiceState === 'idle' && (
                        <p>{language === 'en' ? 'Tap "Listening" to start speaking in Kannada' : '"ಆಲಿಸುತ್ತಿದೆ" ಟ್ಯಾಪ್ ಮಾಡಿ ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಲು'}</p>
                    )}
                    {voiceState === 'listening' && (
                        <p className="listening-text">{language === 'en' ? '🎤 Speak now in Kannada...' : '🎤 ಈಗ ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ...'}</p>
                    )}
                    {voiceState === 'talking' && (
                        <p className="talking-text">{language === 'en' ? '🔊 Aditya is responding...' : '🔊 ಆದಿತ್ಯ ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತಿದ್ದಾರೆ...'}</p>
                    )}
                    {loading && (
                        <p className="loading-text">{language === 'en' ? '⏳ Processing...' : '⏳ ಸಂಸ್ಕರಿಸಲಾಗುತ್ತಿದೆ...'}</p>
                    )}
                </div>
            </div>

            {/* Chat History */}
            {messages.length > 0 && (
                <div className="chat-history-section">
                    <h3 className="chat-history-title">
                        {language === 'en' ? 'Conversation History' : 'ಸಂಭಾಷಣೆ ಇತಿಹಾಸ'}
                    </h3>
                    <div className="messages-list-new">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`message-bubble-new ${msg.sender}`}>
                                <div className="message-sender">
                                    {msg.sender === 'user' ? '👤' : '✨'}
                                    <span>{msg.sender === 'user' ? (language === 'en' ? 'You' : 'ನೀವು') : 'Aditya'}</span>
                                </div>
                                <div className="message-text-new">{msg.text}</div>
                                {msg.translation && (
                                    <div className="message-translation-new">{msg.translation}</div>
                                )}
                            </div>
                        ))}
                        <div ref={chatEndRef} />
                    </div>
                </div>
            )}
        </div>
    );
}
