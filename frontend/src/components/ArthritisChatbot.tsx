import { useState, useEffect, useRef, useCallback } from 'react';
import { useApi } from '../hooks/useApi';

interface Message {
    id: string;
    text_en: string;
    text_kn: string;
    sender: 'user' | 'ai';
}

interface ArthritisChatbotProps {
    language: 'en' | 'kn';
}

export default function ArthritisChatbot({ language }: ArthritisChatbotProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text_en: 'Hello! I am your Arthritis Assistant. How can I help you today?',
            text_kn: 'ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಅಸ್ಥಿಸಂಧಿವಾತದ ಸಹಾಯಕ. ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?',
            sender: 'ai'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [ttsLanguage, setTtsLanguage] = useState<'en' | 'kn'>(language);
    const { sendArthritisChatMessage, loading } = useApi();
    const chatEndRef = useRef<HTMLDivElement>(null);

    // Sync TTS language with global language when it changes
    useEffect(() => {
        setTtsLanguage(language);
    }, [language]);

    // Scroll to bottom when messages change
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const speak = useCallback((text: string, lang: 'en' | 'kn') => {
        const synth = window.speechSynthesis;
        if (!synth) return;

        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);

        const voices = synth.getVoices();
        let selectedVoice: SpeechSynthesisVoice | undefined;

        if (lang === 'kn') {
            selectedVoice = voices.find(v => v.lang === 'kn-IN' || v.lang.startsWith('kn'));
            if (!selectedVoice) {
                selectedVoice = voices.find(v => v.lang === 'hi-IN' || v.lang.startsWith('hi'));
            }
        } else {
            selectedVoice = voices.find(v => v.lang.startsWith('en'));
        }

        if (selectedVoice) utterance.voice = selectedVoice;
        utterance.lang = lang === 'kn' ? 'kn-IN' : 'en-US';
        utterance.rate = 0.9;

        synth.speak(utterance);
    }, []);

    const handleSend = async () => {
        if (!inputValue.trim() || loading) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            text_en: inputValue,
            text_kn: inputValue, // In a real app we might translate this too
            sender: 'user'
        };

        setMessages(prev => [...prev, userMsg]);
        setInputValue('');

        const response = await sendArthritisChatMessage(inputValue);
        if (response) {
            // Safety: Ensure response fields are strings
            const text_en = typeof response.response_en === 'string'
                ? response.response_en
                : JSON.stringify(response.response_en);
            const text_kn = typeof response.response_kn === 'string'
                ? response.response_kn
                : JSON.stringify(response.response_kn);

            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                text_en,
                text_kn,
                sender: 'ai'
            };
            setMessages(prev => [...prev, aiMsg]);

            // Auto-speak the response in the selected language
            speak(ttsLanguage === 'en' ? text_en : text_kn, ttsLanguage);
        }
    };

    return (
        <div className="chatbot-container">
            <div className="chatbot-header">
                <div className="header-info">
                    <span className="bot-icon">✨</span>
                    <div>
                        <h3>Arthritis Assistant</h3>
                        <p>General Information & Education</p>
                    </div>
                </div>
                <div className="tts-toggle">
                    <span className="toggle-label">Voice:</span>
                    <div className="toggle-buttons">
                        <button
                            className={`toggle-btn ${ttsLanguage === 'en' ? 'active' : ''}`}
                            onClick={() => setTtsLanguage('en')}
                        >
                            English
                        </button>
                        <button
                            className={`toggle-btn ${ttsLanguage === 'kn' ? 'active' : ''}`}
                            onClick={() => setTtsLanguage('kn')}
                        >
                            ಕನ್ನಡ
                        </button>
                    </div>
                </div>
            </div>

            <div className="chatbot-messages">
                {messages.map((msg) => (
                    <div key={msg.id} className={`chat-message ${msg.sender}`}>
                        <div className="message-content">
                            {msg.sender === 'ai' && (
                                <>
                                    <div className="text-en">{msg.text_en}</div>
                                    <div className="text-kn">{msg.text_kn}</div>
                                    <button
                                        className="speak-btn"
                                        onClick={() => speak(ttsLanguage === 'en' ? msg.text_en : msg.text_kn, ttsLanguage)}
                                        title="Speak message"
                                    >
                                        🔊
                                    </button>
                                </>
                            )}
                            {msg.sender === 'user' && <div>{msg.text_en}</div>}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="chat-message ai loading">
                        <div className="message-content">
                            <div className="typing-indicator">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <div className="chatbot-input">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask about arthritis..."
                    disabled={loading}
                />
                <button
                    className="send-btn"
                    onClick={handleSend}
                    disabled={!inputValue.trim() || loading}
                >
                    {loading ? '...' : 'Send'}
                </button>
            </div>
        </div>
    );
}
