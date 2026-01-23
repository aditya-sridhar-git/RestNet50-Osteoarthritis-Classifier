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

export default function Discussions({ patientId, language: uiLanguage }: DiscussionsProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [ttsLanguage, setTtsLanguage] = useState<'en' | 'kn'>(uiLanguage);
    const { sendChatMessage, loading } = useApi();
    const chatEndRef = useRef<HTMLDivElement>(null);

    // Sync TTS language with global language when it changes
    useEffect(() => {
        setTtsLanguage(uiLanguage);
    }, [uiLanguage]);

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

    const handleSendMessage = async () => {
        if (!inputValue.trim() || loading) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            text: inputValue,
            sender: 'user'
        };
        setMessages(prev => [...prev, userMsg]);
        setInputValue('');

        const aiResponse = await sendChatMessage(patientId, inputValue);
        if (aiResponse) {
            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: aiResponse.response_kn,
                sender: 'ai',
                translation: aiResponse.response_en
            };
            setMessages(prev => [...prev, aiMsg]);

            // Speak the response in the selected voice language
            const textToSpeak = ttsLanguage === 'kn' ? aiResponse.response_kn : aiResponse.response_en;
            speak(textToSpeak, ttsLanguage);
        }
    };

    return (
        <div className="discussions-container-new">
            <div className="discussions-header">
                <div className="header-info">
                    <h3>{uiLanguage === 'en' ? 'Personal Consultation' : 'ವೈಯಕ್ತಿಕ ಸಮಾಲೋಚನೆ'}</h3>
                    <p>{uiLanguage === 'en' ? 'Chat with Aditya about your health' : 'ನಿಮ್ಮ ಆರೋಗ್ಯದ ಬಗ್ಗೆ ಆದಿತ್ಯ ಅವರೊಂದಿಗೆ ಚರ್ಚಿಸಿ'}</p>
                </div>
                <div className="tts-toggle">
                    <span className="toggle-label">{uiLanguage === 'en' ? 'Voice:' : 'ಧ್ವನಿ:'}</span>
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

            <div className="messages-list-new">
                {messages.length === 0 && (
                    <div className="empty-chat">
                        <span className="empty-icon">💬</span>
                        <p>{uiLanguage === 'en' ? 'Start a conversation with Aditya' : 'ಆದಿತ್ಯ ಅವರೊಂದಿಗೆ ಸಂಭಾಷಣೆ ಪ್ರಾರಂಭಿಸಿ'}</p>
                    </div>
                )}
                {messages.map((msg) => (
                    <div key={msg.id} className={`message-bubble-new ${msg.sender}`}>
                        <div className="message-sender">
                            {msg.sender === 'user' ? '👤' : '✨'}
                            <span>{msg.sender === 'user' ? (uiLanguage === 'en' ? 'You' : 'ನೀವು') : 'Aditya'}</span>
                        </div>
                        <div className="message-text-new">{msg.text}</div>
                        {msg.translation && (
                            <div className="message-translation-new">{msg.translation}</div>
                        )}
                        {msg.sender === 'ai' && (
                            <button
                                className="speak-btn-mini"
                                onClick={() => speak(ttsLanguage === 'kn' ? msg.text : (msg.translation || msg.text), ttsLanguage)}
                            >
                                🔊
                            </button>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className="message-bubble-new ai loading">
                        <div className="typing-indicator">
                            <span></span><span></span><span></span>
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
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder={uiLanguage === 'en' ? 'Type your message...' : 'ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ...'}
                    disabled={loading}
                />
                <button
                    className="send-btn"
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || loading}
                >
                    {loading ? '...' : (uiLanguage === 'en' ? 'Send' : 'ಕಳುಹಿಸು')}
                </button>
            </div>
        </div>
    );
}
