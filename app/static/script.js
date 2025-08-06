// Application State
let currentPage = 'homepage';
let currentUser = null;
let selectedCategories = [];
const API_BASE_URL = 'http://localhost:5000';
const TRENDING_CATEGORIES_LIMIT = 5;

// Categories list matching backend ALL_CATEGORIES
const allCategories = [
    "AI/ML & Data Science", "Web Development", "Mobile Development",
    "Software Engineering", "Game Development", "Design & Creative",
    "Digital Marketing", "Content & Writing", "System Admin & DevOps",
    "IT & Support", "Business & Consulting", "Engineering & Architecture",
    "Admin & Data Entry"
];

// Color classes for progress bars (matching HTML)
const progressBarColors = ['blue', 'purple', 'pink', 'cyan', 'orange'];

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function truncateDescription(description, maxLength = 150) {
    if (!description) return '';
    if (description.length <= maxLength) return description;
    return description.substring(0, maxLength) + '...';
}

function showMessage(text, type = 'success') {
    const toast = document.getElementById('message-toast');
    const textElement = toast.querySelector('.message-text');

    toast.className = `message-toast ${type}`;
    textElement.textContent = text;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 5000);
}

async function updateTrendingCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/trending_categories`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch trending categories');
        }

        const trendingData = await response.json();
        const categoryList = document.querySelector('.category-list');

        if (!categoryList) {
            console.error('Category list element not found');
            return;
        }

        // Clear existing content
        categoryList.innerHTML = '';

        // Map API data to HTML
        trendingData.forEach((category, index) => {
            // Calculate progress width (normalize percentage to 0-100 scale)
            const percentage = parseFloat(category.change.replace('+', '').replace('%', ''));
            const normalizedWidth = Math.min((percentage / 400) * 100, 100); // Cap at 100%

            const categoryItem = document.createElement('div');
            categoryItem.className = 'category-item';
            categoryItem.innerHTML = `
                <div class="category-info">
                    <span class="category-name">${category.name}</span>
                    <div class="category-meta">
                        <span class="category-badge positive">${category.change}</span>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${progressBarColors[index]}" style="width: ${normalizedWidth}%"></div>
                </div>
            `;
            categoryList.appendChild(categoryItem);
        });

    } catch (error) {
        console.error('Error fetching trending categories:', error);
        showMessage('Failed to load trending categories', 'error');
    }
}

function navigateToPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.getElementById(`${page === 'homepage' ? 'homepage' : page + '-page'}`).classList.remove('hidden');

    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (currentUser && page !== 'homepage' && page !== 'auth') {
        sidebar.classList.remove('hidden');
        mainContent.classList.add('with-sidebar');
        updateSidebarState(page);
    } else {
        sidebar.classList.add('hidden');
        mainContent.classList.remove('with-sidebar');
    }

    currentPage = page;
    onPageChange(page);
}

function updateSidebarState(page) {
    document.querySelectorAll('.sidebar-nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    if (page === 'dashboard') {
        document.getElementById('nav-dashboard').classList.add('active');
    } else if (page === 'preferences') {
        document.getElementById('nav-preferences').classList.add('active');
    }

    document.getElementById('sidebar-user-email').textContent = currentUser ? currentUser.email : '';

    const preferencesSection = document.getElementById('sidebar-preferences');
    const preferencesList = document.getElementById('sidebar-preferences-list');

    if (currentUser && currentUser.preferences && currentUser.preferences.length > 0) {
        preferencesSection.classList.remove('hidden');
        preferencesList.innerHTML = currentUser.preferences
            .map(pref => `<span class="sidebar-preference-tag">${pref}</span>`)
            .join('');
    } else {
        preferencesSection.classList.add('hidden');
    }
}

async function checkCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/current_user`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (response.ok) {
            currentUser = { id: data.user_id, email: data.email, preferences: [] };
            await fetchUserPreferences();
            updateSidebarState(currentPage);
            if (currentPage === 'homepage') {
                navigateToPage('dashboard');
            }
        } else {
            currentUser = null;
            navigateToPage('homepage');
        }
    } catch (error) {
        console.error('Error checking current user:', error);
        currentUser = null;
        navigateToPage('homepage');
    }
}

async function fetchUserPreferences() {
    if (!currentUser) return;
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/${currentUser.id}/preferences`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (response.ok) {
            currentUser.preferences = data.preferences || [];
            selectedCategories = [...currentUser.preferences];
        }
    } catch (error) {
        console.error('Error fetching preferences:', error);
    }
}

async function handleAuth(email, password, isLogin = false) {
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters', 'error');
        return;
    }

    const csrfTokenElement = document.querySelector('meta[name="csrf-token"]');
    if (!csrfTokenElement || !csrfTokenElement.content) {
        console.error('CSRF token not found or empty');
        showMessage('Authentication error: CSRF token missing', 'error');
        return;
    }

    try {
        const csrfToken = csrfTokenElement.content;
        const endpoint = isLogin ? `${API_BASE_URL}/api/login` : `${API_BASE_URL}/api/register`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();

        if (response.ok) {
            currentUser = { id: data.user_id, email, preferences: [] };
            showMessage(isLogin ? 'Login successful!' : 'Registration successful!');
            await fetchUserPreferences();
            navigateToPage(isLogin ? 'dashboard' : 'preferences');
        } else {
            console.error(`Auth error: ${response.status} - ${data.message}`);
            showMessage(data.message || 'Authentication failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Auth error:', error);
        showMessage('Network error. Please check your connection and try again.', 'error');
    }
}

async function handleLogout() {
    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const response = await fetch(`${API_BASE_URL}/api/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            }
        });
        const data = await response.json();
        if (response.ok) {
            currentUser = null;
            selectedCategories = [];
            showMessage(data.message);
            navigateToPage('homepage');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showMessage('An error occurred during logout', 'error');
    }
}

// Preferences Functions
function updatePreferencesDisplay() {
    const currentPrefs = document.getElementById('current-preferences');
    const counter = document.getElementById('selection-counter');
    const counterText = counter.querySelector('.counter-text');
    const saveBtn = document.getElementById('save-preferences');
    const skipBtn = document.getElementById('skip-to-dashboard');

    if (selectedCategories.length > 0) {
        currentPrefs.innerHTML = selectedCategories
            .map(cat => `<span class="preference-tag">${cat}</span>`)
            .join('');
    } else {
        currentPrefs.innerHTML = '<span class="no-preferences">None selected</span>';
    }

    counterText.textContent = `${selectedCategories.length}/3 categories selected`;
    counter.className = 'selection-counter';
    if (selectedCategories.length === 0) {
        counter.classList.add('empty');
    } else if (selectedCategories.length <= 3) {
        counter.classList.add('valid');
    } else {
        counter.classList.add('invalid');
    }

    saveBtn.disabled = selectedCategories.length === 0;
    skipBtn.classList.toggle('hidden', !(currentUser && currentUser.preferences.length > 0));

    allCategories.forEach(category => {
        const option = document.querySelector(`[data-category="${category}"]`);
        if (!option) return;

        const isSelected = selectedCategories.includes(category);
        const canSelect = selectedCategories.length < 3 || isSelected;

        option.className = 'category-option';
        if (isSelected) {
            option.classList.add('selected');
        } else if (!canSelect) {
            option.classList.add('disabled');
        }
    });
}

function toggleCategory(category) {
    if (selectedCategories.includes(category)) {
        selectedCategories = selectedCategories.filter(c => c !== category);
    } else if (selectedCategories.length < 3) {
        selectedCategories.push(category);
    }
    updatePreferencesDisplay();
}

async function savePreferences() {
    if (selectedCategories.length === 0 || selectedCategories.length > 3) {
        showMessage('Please select 1-3 categories', 'error');
        return;
    }

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        const response = await fetch(`${API_BASE_URL}/api/users/${currentUser.id}/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken
            },
            body: JSON.stringify({ categories: selectedCategories })
        });
        const data = await response.json();

        if (response.ok) {
            currentUser.preferences = [...selectedCategories];
            showMessage('Preferences saved successfully!');
            navigateToPage('dashboard');
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        console.error('Error saving preferences:', error);
        showMessage('An error occurred while saving preferences', 'error');
    }
}

// Dashboard Functions
async function updateDashboard() {
    const welcomeMsg = document.getElementById('dashboard-welcome');
    const preferencesContent = document.getElementById('dashboard-preferences-content');
    const gigsSection = document.getElementById('gigs-section');
    const gigsList = document.getElementById('gigs-list');
    const noGigsMessage = document.getElementById('no-gigs-message');

    welcomeMsg.textContent = `Welcome back, ${currentUser.email}!`;

    if (currentUser.preferences && currentUser.preferences.length > 0) {
        preferencesContent.innerHTML = `
            <div class="preferences-header-with-btn">
                <div>
                    <p class="preferences-label">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <polyline points="22,7 13.5,15.5 8.5,10.5 2,17"/>
                            <polyline points="16,7 22,7 22,13"/>
                        </svg>
                        Your focus areas:
                    </p>
                    <div class="preferences-tags">
                        ${currentUser.preferences.map(pref => 
                            `<span class="preference-tag">${pref}</span>`
                        ).join('')}
                    </div>
                </div>
                <button class="btn-outline" onclick="navigateToPage('preferences')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                        <circle cx="12" cy="12" r="3"/>
                    </svg>
                    Update
                </button>
            </div>
        `;

        gigsSection.classList.remove('hidden');

        try {
            const response = await fetch(`${API_BASE_URL}/api/gigs/recommended/${currentUser.id}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok && data.gigs.length > 0) {
                gigsList.innerHTML = data.gigs.map(gig => `
                    <div class="gig-card">
                        <div class="gig-header">
                            <h3 class="gig-title">
                                <a href="${gig.link}" target="_blank" rel="noopener noreferrer">
                                    ${gig.title}
                                </a>
                            </h3>
                            <div class="gig-meta">
                                <span class="gig-category">${gig.category}</span>
                                <div class="gig-date">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                                        <line x1="16" y1="2" x2="16" y2="6"/>
                                        <line x1="8" y1="2" x2="8" y2="6"/>
                                        <line x1="3" y1="10" x2="21" y2="10"/>
                                    </svg>
                                    ${formatDate(gig.published_at)}
                                </div>
                                ${gig.budget_amount ? `
                                    <div class="gig-budget">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                            <line x1="12" y1="2" x2="12" y2="22"/>
                                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                                        </svg>
                                        ${gig.budget_amount} ${gig.budget_currency}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        <div class="gig-content">
                            <p class="gig-description">${truncateDescription(gig.description)}</p>
                            <div class="gig-actions">
                                <a href="${gig.link}" target="_blank" rel="noopener noreferrer" class="gig-link">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M7 17L17 7"/><path d="M7 7h10v10"/>
                                    </svg>
                                    View Opportunity
                                </a>
                            </div>
                        </div>
                    </div>
                `).join('');
                gigsList.classList.remove('hidden');
                noGigsMessage.classList.add('hidden');
            } else {
                gigsList.classList.add('hidden');
                noGigsMessage.classList.remove('hidden');
                showMessage(data.message, 'info');
            }
        } catch (error) {
            console.error('Error fetching gigs:', error);
            gigsList.classList.add('hidden');
            noGigsMessage.classList.remove('hidden');
            showMessage('Error fetching recommended gigs', 'error');
        }
    } else {
        preferencesContent.innerHTML = `
            <div class="no-preferences-content">
                <div class="no-preferences-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
                    </svg>
                </div>
                <p class="no-preferences-title">You haven't set any preferences yet. Let's personalize your experience!</p>
                <button class="btn-primary" onclick="navigateToPage('preferences')">
                    Set Your Preferences
                </button>
            </div>
        `;
        gigsSection.classList.add('hidden');
    }
}

// Homepage Functions
async function updateHomepageStats() {
    try {
        const statsResponse = await fetch(`${API_BASE_URL}/api/stats`);
        if (!statsResponse.ok) {
            throw new Error('Failed to fetch stats');
        }

        const statsData = await statsResponse.json();

        // Update each stat value
        document.querySelector('[data-stat="active_gigs"]').textContent =
            statsData.active_gigs?.toLocaleString() ?? 'N/A';
        document.querySelector('[data-stat="avg_budget"]').textContent =
            statsData.avg_budget ? `$${statsData.avg_budget.toLocaleString()}` : 'N/A';
        document.querySelector('[data-stat="freelancers"]').textContent =
            statsData.freelancers?.toLocaleString() ?? 'N/A';
        const successRateElement = document.querySelector('[data-stat="sent_gigs"]');
        if (successRateElement) {
            successRateElement.textContent =
                statsData.delivered_gigs ? `${statsData.delivered_gigs}` : 'N/A';
        }

        // Update trending categories
        await updateTrendingCategories();

    } catch (error) {
        console.error('Error updating stats:', error);
        showMessage('Failed to load stats data', 'error');
    }
}

// Initialize Categories Grid
function initializeCategoriesGrid() {
    const grid = document.getElementById('categories-grid');
    grid.innerHTML = allCategories.map(category => `
        <div class="category-option" data-category="${category}" onclick="toggleCategory('${category}')">
            <div class="category-checkbox">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="m9 12 2 2 4-4"/>
                </svg>
            </div>
            <label class="category-label">${category}</label>
        </div>
    `).join('');
}

// Auth Page Functions
function toggleAuthMode() {
    const isLogin = document.getElementById('auth-form').dataset.mode === 'login';
    const newMode = isLogin ? 'register' : 'login';

    document.getElementById('auth-form').dataset.mode = newMode;

    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    const formTitle = document.getElementById('auth-form-title');
    const submitBtn = document.getElementById('auth-submit');
    const toggleBtn = document.getElementById('toggle-auth');
    const passwordHelp = document.getElementById('password-help');
    const benefits = document.getElementById('auth-benefits');

    if (newMode === 'login') {
        title.textContent = 'Welcome Back';
        subtitle.textContent = 'Sign in to access your personalized dashboard';
        formTitle.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16,17 21,12 16,7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Sign In
        `;
        submitBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16,17 21,12 16,7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Sign In
        `;
        toggleBtn.textContent = "Don't have an account? Sign up instead";
        passwordHelp.style.display = 'none';
        benefits.style.display = 'none';
    } else {
        title.textContent = 'Join StreamLance';
        subtitle.textContent = 'Start discovering your perfect freelance opportunities';
        formTitle.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="8.5" cy="7" r="4"/>
                <path d="m20 8 2 2-3 3L10 9l2-2z"/>
            </svg>
            Create Account
        `;
        submitBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="8.5" cy="7" r="4"/>
                <path d="m20 8 2 2-3 3L10 9l2-2z"/>
            </svg>
            Create Account
        `;
        toggleBtn.textContent = 'Already have an account? Sign in instead';
        passwordHelp.style.display = 'block';
        benefits.style.display = 'block';
    }
}

// Page-specific Updates
function onPageChange(page) {
    switch(page) {
        case 'homepage':
            updateHomepageStats();
            updateActivityList();
            break;
        case 'preferences':
            selectedCategories = currentUser && currentUser.preferences ? [...currentUser.preferences] : [];
            updatePreferencesDisplay();
            break;
        case 'dashboard':
            updateDashboard();
            break;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeCategoriesGrid();
    checkCurrentUser();

    document.getElementById('get-started-btn').addEventListener('click', () => {
        navigateToPage('auth');
    });

    document.getElementById('back-to-home').addEventListener('click', () => {
        navigateToPage('homepage');
    });

    document.getElementById('auth-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const isLogin = e.target.dataset.mode === 'login';
        handleAuth(email, password, isLogin);
    });

    document.getElementById('toggle-auth').addEventListener('click', toggleAuthMode);

    document.getElementById('save-preferences').addEventListener('click', savePreferences);

    document.getElementById('skip-to-dashboard').addEventListener('click', () => {
        navigateToPage('dashboard');
    });

    document.getElementById('nav-dashboard').addEventListener('click', () => {
        navigateToPage('dashboard');
    });

    document.getElementById('nav-preferences').addEventListener('click', () => {
        selectedCategories = currentUser && currentUser.preferences ? [...currentUser.preferences] : [];
        updatePreferencesDisplay();
        navigateToPage('preferences');
    });

    document.getElementById('logout-btn').addEventListener('click', handleLogout);

    document.getElementById('adjust-preferences').addEventListener('click', () => {
        navigateToPage('preferences');
    });

    document.getElementById('auth-form').dataset.mode = 'register';
});

// Export functions for global access
window.navigateToPage = navigateToPage;
window.toggleCategory = toggleCategory;
window.savePreferences = savePreferences;
window.handleLogout = handleLogout;
window.updateDashboard = updateDashboard;
window.updateTrendingCategories = updateTrendingCategories;