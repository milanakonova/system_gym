function showRegister() {
    document.getElementById('registerModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('registerModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('registerModal');
    if (event.target === modal) {
        closeModal();
    }
}

async function registerUser(event) {
    event.preventDefault();
    
    const userData = {
        username: document.getElementById('regUsername').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        full_name: document.getElementById('regFullName').value,
        phone: document.getElementById('regPhone').value,
        role: document.getElementById('regRole').value
    };
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Пользователь ${data.username} успешно зарегистрирован!`);
            closeModal();
            window.location.href = '/login';
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при регистрации');
    }
}

async function loginUser(event) {
    event.preventDefault();
    
    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            alert('Вход выполнен успешно!');
            window.location.href = '/dashboard';
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.detail}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка при входе');
    }
}

function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token && window.location.pathname !== '/' && window.location.pathname !== '/login') {
        window.location.href = '/login';
    }
    return token;
}

async function getCurrentUser() {
    const token = checkAuth();
    if (!token) return null;
    
    try {
        const response = await fetch('/api/users/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return null;
        }
    } catch (error) {
        console.error('Ошибка:', error);
        return null;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/';
}

async function loadClientDashboard(user) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/clients/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const clientData = await response.json();
            document.getElementById('visitsLeft').textContent = clientData.visits_left;
            document.getElementById('hasSubscription').textContent = 
                clientData.has_subscription ? 'Активен' : 'Неактивен';
        }
    } catch (error) {
        console.error('Ошибка при загрузке данных клиента:', error);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/dashboard') {
        loadDashboard();
    }
});
