document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const passwordInput = document.getElementById('password');
    const loginError = document.getElementById('login-error');
    const loginScreen = document.getElementById('login-screen');
    const adminPanel = document.getElementById('admin-panel');
    const logoutBtn = document.getElementById('logout-btn');

    // Check if logged in
    if (sessionStorage.getItem('isAdmin') === 'true') {
        showAdminPanel();
    }

    // Login
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (passwordInput.value === 'admin123') {
            sessionStorage.setItem('isAdmin', 'true');
            showAdminPanel();
        } else {
            loginError.classList.remove('d-none');
        }
    });

    // Logout
    logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        sessionStorage.removeItem('isAdmin');
        loginScreen.classList.remove('d-none');
        adminPanel.classList.add('d-none');
    });

    function showAdminPanel() {
        loginScreen.classList.add('d-none');
        adminPanel.classList.remove('d-none');

        window.db.openDatabase().then(() => {
            loadDashboard();
            loadHotels();
            setupEventListeners();
        }).catch(error => {
            console.error("Error initializing database:", error);
            showToast('Error', 'Failed to load admin data.', 'danger');
        });
    }

    function setupEventListeners() {
        // Sidebar navigation
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                if (link.id !== 'logout-btn') {
                    e.preventDefault();
                    const targetId = link.getAttribute('data-target');

                    document.querySelectorAll('.content-section').forEach(section => {
                        section.classList.add('d-none');
                    });
                    document.getElementById(targetId).classList.remove('d-none');

                    navLinks.forEach(nav => nav.classList.remove('active'));
                    link.classList.add('active');
                }
            });
        });

        // Hotel form
        const hotelForm = document.getElementById('hotel-form');
        hotelForm.addEventListener('submit', handleHotelFormSubmit);

        // Reset modal on close
        const addHotelModal = document.getElementById('addHotelModal');
        addHotelModal.addEventListener('hidden.bs.modal', () => {
            hotelForm.reset();
            document.getElementById('hotel-id').value = '';
            document.getElementById('hotelModalTitle').textContent = 'Add New Hotel';
        });
    }

    async function loadDashboard() {
        const hotels = await window.db.getAllHotels();
        const dashboard = document.querySelector('#dashboard .row');
        dashboard.innerHTML = `
            <div class="col-md-3"><div class="card p-3"><h5 class="card-title">Total Hotels</h5><p class="card-text">${hotels.length}</p></div></div>
            <div class="col-md-3"><div class="card p-3"><h5 class="card-title">Total Bookings</h5><p class="card-text">125</p></div></div>
            <div class="col-md-3"><div class="card p-3"><h5 class="card-title">Total Users</h5><p class="card-text">42</p></div></div>
            <div class="col-md-3"><div class="card p-3"><h5 class="card-title">Revenue</h5><p class="card-text">$25,600</p></div></div>
        `;
    }

    async function loadHotels() {
        const hotels = await window.db.getAllHotels();
        const tableBody = document.getElementById('hotel-table-body');
        tableBody.innerHTML = '';
        hotels.forEach(hotel => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${hotel.id}</td>
                <td>${hotel.name}</td>
                <td>${hotel.location}</td>
                <td>$${hotel.price}</td>
                <td>${hotel.rating}</td>
                <td>
                    <button class="btn btn-sm btn-info btn-edit" data-id="${hotel.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-danger btn-delete" data-id="${hotel.id}"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tableBody.appendChild(row);
        });

        // Add event listeners for edit/delete
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', handleEditHotel);
        });
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', handleDeleteHotel);
        });
    }

    async function handleHotelFormSubmit(e) {
        e.preventDefault();
        const hotelId = document.getElementById('hotel-id').value;

        const hotel = {
            name: document.getElementById('hotel-name').value,
            location: document.getElementById('hotel-location').value,
            price: parseFloat(document.getElementById('hotel-price').value),
            rating: parseInt(document.getElementById('hotel-rating').value),
            image: document.getElementById('hotel-image').value,
            description: document.getElementById('hotel-description').value,
            amenities: document.getElementById('hotel-amenities').value.split(',').map(s => s.trim()),
            // Dummy data for fields not in the form
            reviewScore: (Math.random() * (10 - 7) + 7).toFixed(1),
            reviewText: "Good",
            tags: ["new"]
        };

        try {
            if (hotelId) {
                hotel.id = parseInt(hotelId);
                await window.db.updateHotel(hotel);
                showToast('Success', 'Hotel updated successfully.', 'success');
            } else {
                await window.db.addHotel(hotel);
                showToast('Success', 'Hotel added successfully.', 'success');
            }

            bootstrap.Modal.getInstance(document.getElementById('addHotelModal')).hide();
            loadHotels();
            loadDashboard();
        } catch (error) {
            console.error("Error saving hotel:", error);
            showToast('Error', 'Failed to save hotel.', 'danger');
        }
    }

    async function handleEditHotel(e) {
        const hotelId = parseInt(e.currentTarget.getAttribute('data-id'));
        const hotel = await window.db.getHotelById(hotelId);

        if (hotel) {
            document.getElementById('hotel-id').value = hotel.id;
            document.getElementById('hotel-name').value = hotel.name;
            document.getElementById('hotel-location').value = hotel.location;
            document.getElementById('hotel-price').value = hotel.price;
            document.getElementById('hotel-rating').value = hotel.rating;
            document.getElementById('hotel-image').value = hotel.image;
            document.getElementById('hotel-description').value = hotel.description;
            document.getElementById('hotel-amenities').value = hotel.amenities.join(', ');
            document.getElementById('hotelModalTitle').textContent = 'Edit Hotel';

            new bootstrap.Modal(document.getElementById('addHotelModal')).show();
        }
    }

    async function handleDeleteHotel(e) {
        const hotelId = parseInt(e.currentTarget.getAttribute('data-id'));
        if (confirm(`Are you sure you want to delete hotel #${hotelId}?`)) {
            try {
                await window.db.deleteHotel(hotelId);
                showToast('Success', 'Hotel deleted successfully.', 'success');
                loadHotels();
                loadDashboard();
            } catch (error) {
                console.error("Error deleting hotel:", error);
                showToast('Error', 'Failed to delete hotel.', 'danger');
            }
        }
    }
});

// Toast Notification
function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('notificationToast');
    const toast = new bootstrap.Toast(toastEl);

    document.getElementById('toast-title').textContent = title;
    document.getElementById('toast-body').textContent = message;

    toastEl.classList.remove('bg-info', 'bg-success', 'bg-warning', 'bg-danger');
    toastEl.classList.add(`bg-${type}`, 'text-white');

    // Ensure toast text is readable on dark backgrounds
    if (type === 'info' || type === 'light' || !type) {
        toastEl.classList.remove('text-white');
    } else {
        toastEl.classList.add('text-white');
    }


    toast.show();
}
