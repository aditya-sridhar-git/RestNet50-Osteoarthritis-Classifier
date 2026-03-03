import { useRef, useState, type DragEvent } from 'react';

interface ImageUploadProps {
    onFileSelect: (file: File) => void;
    selectedFile: File | null;
    previewUrl: string | null;
    onRemove: () => void;
}

export default function ImageUpload({
    onFileSelect,
    selectedFile,
    previewUrl,
    onRemove
}: ImageUploadProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isDragOver, setIsDragOver] = useState(false);

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            onFileSelect(file);
        }
    };

    const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragOver(true);
    };

    const handleDragLeave = () => {
        setIsDragOver(false);
    };

    const handleDrop = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            onFileSelect(file);
        }
    };

    if (selectedFile && previewUrl) {
        return (
            <div className="preview-container">
                <img src={previewUrl} alt="X-ray preview" className="preview-image" />
                <button className="remove-btn" onClick={onRemove} aria-label="Remove image">
                    ×
                </button>
            </div>
        );
    }

    return (
        <div className="upload-card">
            <div
                className={`upload-area ${isDragOver ? 'dragover' : ''}`}
                onClick={handleClick}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <div className="upload-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                </div>
                <p className="upload-text">Drop your X-ray image here</p>
                <p className="upload-hint">or click to browse</p>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    hidden
                />
            </div>
        </div>
    );
}
