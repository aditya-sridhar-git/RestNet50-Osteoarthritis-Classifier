// ===== DOM Elements =====
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const removeBtn = document.getElementById('removeBtn');
const patientIdInput = document.getElementById('patientId');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');

// ===== State =====
let selectedFile = null;

// ===== API Configuration =====
const API_BASE = 'http://127.0.0.1:5000';

// ===== Event Listeners =====

// Click to upload
uploadArea.addEventListener('click', () => fileInput.click());

// File select
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    }
});

// Remove image
removeBtn.addEventListener('click', () => {
    selectedFile = null;
    previewContainer.classList.remove('active');
    uploadArea.style.display = 'block';
    fileInput.value = '';
    updateAnalyzeButton();
});

// Patient ID input
patientIdInput.addEventListener('input', updateAnalyzeButton);

// Analyze button
analyzeBtn.addEventListener('click', analyzeImage);

// ===== Functions =====

function handleFile(file) {
    selectedFile = file;

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.classList.add('active');
        uploadArea.style.display = 'none';
        updateAnalyzeButton();
    };
    reader.readAsDataURL(file);
}

function updateAnalyzeButton() {
    const hasFile = selectedFile !== null;
    const hasPatientId = patientIdInput.value.trim() !== '';
    analyzeBtn.disabled = !(hasFile && hasPatientId);
}

async function analyzeImage() {
    if (!selectedFile) return;

    const patientId = patientIdInput.value.trim();

    // Show loading state
    analyzeBtn.classList.add('loading');
    analyzeBtn.disabled = true;

    try {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('user', patientId);

        // Send request
        const response = await fetch(`${API_BASE}/analyze-upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze image. Please make sure the server is running.');
    } finally {
        analyzeBtn.classList.remove('loading');
        updateAnalyzeButton();
    }
}

function displayResults(data) {
    // Show results section with animation
    resultsSection.classList.add('active');

    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Update severity badge
    const severityBadge = document.getElementById('severityBadge');
    severityBadge.textContent = data.severity;
    severityBadge.className = 'severity-badge ' + data.severity.toLowerCase();

    // Update severity meter
    const severityFill = document.getElementById('severityFill');
    const severityLevels = ['Normal', 'Doubtful', 'Mild', 'Moderate', 'Severe'];
    const severityIndex = severityLevels.indexOf(data.severity);
    const severityPercent = ((severityIndex + 1) / severityLevels.length) * 100;

    // Set color based on severity
    const colors = {
        'Normal': '#10b981',
        'Doubtful': '#3b82f6',
        'Mild': '#f59e0b',
        'Moderate': '#f97316',
        'Severe': '#ef4444'
    };

    severityFill.style.width = `${severityPercent}%`;
    severityFill.style.background = colors[data.severity] || colors['Normal'];

    // Update diet recommendations
    const dietList = document.getElementById('dietList');
    dietList.innerHTML = data.diet.map(item => `<li>${item}</li>`).join('');

    // Update exercise recommendations
    const exerciseList = document.getElementById('exerciseList');
    exerciseList.innerHTML = data.exercise.length > 0
        ? data.exercise.map(item => `<li>${item}</li>`).join('')
        : '<li>No specific exercises recommended</li>';

    // Update disclaimer
    document.getElementById('disclaimer').textContent = `⚠️ ${data.disclaimer}`;
}

// ===== Initialize =====
updateAnalyzeButton();
