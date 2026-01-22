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

export default function Discussions({ patientId, language }: DiscussionsProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const { sendChatMessage, loading } = useApi();
    const chatEndRef = useRef<HTMLDivElement>(null);
    const recognitionRef = useRef<any>(null);

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'kn-IN'; // Default to Kannada for STT

            recognition.onresult = async (event: any) => {
                const text = event.results[0][0].transcript;
                setIsListening(false);
                if (text) {
                    await handleSendMessage(text);
                }
            };

            recognition.onerror = () => {
                setIsListening(false);
            };

            recognitionRef.current = recognition;
        }
    }, []);

    // Scroll to bottom when messages change
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const speak = useCallback((text: string, lang: string) => {
        const synth = window.speechSynthesis;
        if (!synth) return;

        // Cancel any ongoing speech
        synth.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === 'kn' ? 'kn-IN' : 'en-US';

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);

        // Find a matching voice if possible
        const voices = synth.getVoices();
        const preferredVoice = voices.find(v => v.lang.startsWith(lang));
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }

        synth.speak(utterance);
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
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            setIsListening(true);
            recognitionRef.current?.start();
        }
    };

    return (
        <div className="results-card discussions-container">
            <div className="discussions-header">
                <h2 className="result-title">
                    {language === 'en' ? 'Voice Discussion' : 'ಧ್ವನಿ ಸಂಭಾಷಣೆ'}
                </h2>
                <div className="ai-badge">✨ AI Assistant (ಕನ್ನಡ)</div>
            </div>

            <div className="chat-window">
                {messages.length === 0 ? (
                    <div className="empty-chat">
                        <div className="pulse-circle">💬</div>
                        <p>{language === 'en' ? 'Tap the microphone and start talking to Aditya in Kannada' : 'ಮೈಕ್ರೊಫೋನ್ ಟ್ಯಾಪ್ ಮಾಡಿ ಮತ್ತು ಆದಿತ್ಯನ ಜೊತೆಗೆ ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಲು ಪ್ರಾರಂಭಿಸಿ'}</p>
                    </div>
                ) : (
                    <div className="messages-list">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`message-bubble ${msg.sender}`}>
                                <div className="message-text">{msg.text}</div>
                                {msg.translation && (
                                    <div className="message-translation">{msg.translation}</div>
                                )}
                            </div>
                        ))}
                        {loading && (
                            <div className="message-bubble ai loading">
                                <span>.</span><span>.</span><span>.</span>
                            </div>
                        )}
                        <div ref={chatEndRef} />
                    </div>
                )}
            </div>

            <div className="chat-controls">
                <button
                    className={`mic-btn ${isListening ? 'listening' : ''} ${isSpeaking ? 'speaking' : ''}`}
                    onClick={toggleListening}
                    disabled={loading || isSpeaking}
                    aria-label="Toggle Microphone"
                >
                    <div className="mic-icon">
                        {isListening ? '🛑' : '🎤'}
                    </div>
                </button>
                <div className="status-text">
                    {isListening && (language === 'en' ? 'Listening...' : 'ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ...')}
                    {isSpeaking && (language === 'en' ? 'Aditya is speaking...' : 'ಆದಿತ್ಯ ಮಾತನಾಡುತ್ತಿದ್ದಾರೆ...')}
                    {!isListening && !isSpeaking && (language === 'en' ? 'Tap to speak' : 'ಮಾತನಾಡಲು ಟ್ಯಾಪ್ ಮಾಡಿ')}
                </div>
            </div>
        </div>
    );
}
