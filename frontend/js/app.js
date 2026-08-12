// =====================================================================
// API Configuration
// =====================================================================
const API_BASE_URL = 'http://localhost:5000';

// =====================================================================
// FORM SUBMISSION & PREDICTION
// =====================================================================
document.getElementById('predictorForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const mathematics = document.getElementById('mathematics').value;
    const physics = document.getElementById('physics').value;
    const chemistry = document.getElementById('chemistry').value;
    const community = document.getElementById('community').value;
    const stream = document.getElementById('stream').value;
    
    // Validate inputs
    if (!mathematics || !physics || !chemistry || !community || !stream) {
        alert('Please fill in all fields');
        return;
    }
    
    // Show loading
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsContent').style.display = 'none';
    document.getElementById('resultsContainer').classList.add('show');
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mathematics: parseFloat(mathematics),
                physics: parseFloat(physics),
                chemistry: parseFloat(chemistry),
                community,
                stream
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error connecting to server. Please ensure the backend is running.');
        console.error(error);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('resultsContent').style.display = 'block';
    }
});

// =====================================================================
// DISPLAY RESULTS
// =====================================================================
function displayResults(data) {
    const cutoffScore = data.cutoff_score;
    const results = data.results;
    
    // Update cutoff score
    document.getElementById('cutoffScore').textContent = cutoffScore.toFixed(2);
    
    // Display colleges
    displayCollegeList('Safe', results.safe, 'safeColleges', 'safeCategory');
    displayCollegeList('Borderline', results.borderline, 'borderlineColleges', 'borderlineCategory');
    displayCollegeList('Dream', results.dream, 'dreamColleges', 'dreamCategory');
    
    // Show/hide no results message
    if (results.total_matched === 0) {
        document.getElementById('noResults').style.display = 'block';
    } else {
        document.getElementById('noResults').style.display = 'none';
    }
}

function displayCollegeList(category, colleges, containerId, categoryId) {
    const container = document.getElementById(containerId);
    const categoryDiv = document.getElementById(categoryId);
    
    if (!colleges || colleges.length === 0) {
        container.innerHTML = '<p style="color: #999; text-align: center;">No colleges in this category</p>';
        categoryDiv.style.display = 'none';
        return;
    }
    
    categoryDiv.style.display = 'block';
    container.innerHTML = colleges.map(college => `
        <div class="college-card">
            <h6>📚 ${college.college_name}</h6>
            <div class="college-info">
                <span><i class="fas fa-book"></i> ${college.branch_name}</span><br>
                <span><i class="fas fa-map-marker-alt"></i> ${college.district || 'N/A'}</span><br>
                <span><i class="fas fa-chair"></i> ${college.available_seats || 0} Seats Available</span>
            </div>
            <div>
                <small style="color: #666;">
                    Your Score: <strong>${parseFloat(college.closing_cutoff) + college.cutoff_difference}</strong> | 
                    College Cutoff: <strong>${college.closing_cutoff}</strong> | 
                    Difference: <strong style="color: ${college.cutoff_difference >= 0 ? '#28a745' : '#dc3545'};">
                        ${college.cutoff_difference > 0 ? '+' : ''}${college.cutoff_difference}
                    </strong>
                </small>
            </div>
            <div style="margin-top: 10px;">
                <span class="badge badge-${category.toLowerCase()}">${college.probability || category}</span>
            </div>
        </div>
    `).join('');
}

// =====================================================================
// CHATBOT FUNCTIONALITY
// =====================================================================
function toggleChatbot() {
    const chatbot = document.getElementById('chatbotContainer');
    const toggle = document.getElementById('chatToggle');
    
    chatbot.classList.toggle('active');
    toggle.classList.toggle('hide');
    
    if (chatbot.classList.contains('active')) {
        document.getElementById('chatInput').focus();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<div class="message-content"><em>Typing...</em></div>';
    document.getElementById('chatMessages').appendChild(typingDiv);
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        document.getElementById('typingIndicator').remove();
        
        if (data.success) {
            addMessageToChat(data.bot_response, 'bot');
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        document.getElementById('typingIndicator').remove();
        addMessageToChat('Sorry, I could not connect to the server. Please check if the backend is running.', 'bot');
        console.error(error);
    }
}

function addMessageToChat(text, sender) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `<div class="message-content">${formatMessage(text)}</div>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function formatMessage(text) {
    // Convert markdown-style formatting to HTML
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')
        .replace(/• /g, '• ');
}

// Allow Enter key to send message
document.getElementById('chatInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// =====================================================================
// SAMPLE QUICK ACTIONS FOR CHATBOT
// =====================================================================
// Add click handlers for quick suggestions if needed