document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const userData = JSON.parse(localStorage.getItem('user'));
    const userDisplayName = document.getElementById('user-display-name');
    const userAvatar = document.getElementById('user-avatar');
    
    if (userData) {
        userDisplayName.textContent = userData.username;
        userAvatar.textContent = userData.username.substring(0, 2).toUpperCase();
    }

    // View Switching Logic
    const navLinks = document.querySelectorAll('.nav-link');
    const views = document.querySelectorAll('.view-section');
    const viewTitle = document.getElementById('view-title');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const viewId = link.getAttribute('data-view');
            if (!viewId) return; // For logout or non-view links
            
            e.preventDefault();
            
            // Update active state
            navLinks.forEach(nl => nl.classList.remove('active'));
            link.classList.add('active');

            // Show current view
            views.forEach(v => v.classList.add('hidden'));
            document.getElementById(`view-${viewId}`).classList.remove('hidden');

            // Update title
            viewTitle.textContent = link.textContent.trim();
            
            // Data loading
            if (viewId === 'dashboard') fetchSummary();
            if (viewId === 'campaigns') fetchCampaigns();
            if (viewId === 'leaderboard') fetchLeaderboard();
        });
    });

    // Logout
    document.getElementById('btn-logout').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    });

    // Modal Control
    const modal = document.getElementById('create-modal');
    document.getElementById('open-create-modal').addEventListener('click', () => modal.style.display = 'flex');
    document.getElementById('close-modal').addEventListener('click', () => modal.style.display = 'none');

    // Create Referral Form
    document.getElementById('create-referral-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const campaign = document.getElementById('campaign-name').value;
        const res = await fetchWithAuth('/api/referrals/', {
            method: 'POST',
            body: JSON.stringify({ campaign })
        });
        if (res.ok) {
            modal.style.display = 'none';
            document.getElementById('campaign-name').value = '';
            fetchCampaigns();
        }
    });

    // --- Data Fetching ---

    async function fetchWithAuth(url, options = {}) {
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        const res = await fetch(url, { ...options, headers });
        if (res.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return res;
    }

    async function fetchSummary() {
        const res = await fetchWithAuth('/api/analytics/summary');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('stat-total-clicks').textContent = data.total_clicks;
            document.getElementById('stat-unique-clicks').textContent = data.unique_clicks;
            document.getElementById('stat-total-conversions').textContent = data.total_conversions;
            document.getElementById('stat-total-value').textContent = `$${data.total_value.toFixed(2)}`;
            document.getElementById('stat-conversion-rate').textContent = `${data.conversion_rate}% rate`;
            
            updateChart(data);
        }
    }

    async function fetchCampaigns() {
        const res = await fetchWithAuth('/api/referrals/');
        if (res.ok) {
            const data = await res.json();
            const tbody = document.getElementById('campaigns-table-body');
            tbody.innerHTML = '';
            data.referrals.forEach(ref => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${ref.campaign}</strong></td>
                    <td><code>${ref.code}</code></td>
                    <td><span class="url-badge">${ref.referral_url}</span></td>
                    <td>${ref.total_clicks}</td>
                    <td>${ref.conversion_rate}%</td>
                    <td><span class="status-badge ${ref.is_active ? 'status-active' : 'status-inactive'}">
                        ${ref.is_active ? 'Active' : 'Paused'}
                    </span></td>
                    <td><button onclick="deactivateLink(${ref.id})" class="btn-logout"><i class="fa-solid fa-ban"></i></button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    async function fetchLeaderboard() {
        const res = await fetch('/api/analytics/leaderboard');
        if (res.ok) {
            const data = await res.json();
            const tbody = document.getElementById('leaderboard-table-body');
            tbody.innerHTML = '';
            data.leaderboard.forEach((item, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>#${index + 1}</strong></td>
                    <td>${item.username}</td>
                    <td>${item.conversions}</td>
                    <td>$${item.total_value.toFixed(2)}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // --- Chart ---
    let myChart;
    function updateChart(data) {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        if (myChart) myChart.destroy();
        
        // Mocking some time series data based on total clicks
        const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        const values = [
            Math.floor(data.total_clicks * 0.1),
            Math.floor(data.total_clicks * 0.3),
            Math.floor(data.total_clicks * 0.2),
            Math.floor(data.total_clicks * 0.4)
        ];

        myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Traffic Volume',
                    data: values,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointBackgroundColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, border: { display: false } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Global action for table buttons
    window.deactivateLink = async (id) => {
        if (!confirm('Are you sure you want to deactivate this link?')) return;
        const res = await fetchWithAuth(`/api/referrals/${id}`, { method: 'DELETE' });
        if (res.ok) fetchCampaigns();
    }

    // Initial Load
    fetchSummary();
});
