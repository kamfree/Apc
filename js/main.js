document.addEventListener('DOMContentLoaded', () => {
    // Initialize database and render page elements
    window.db.openDatabase().then(() => {
        renderHotels();
        setupEventListeners();
        setInitialValues();
        updateFilterOptions();
    }).catch(error => {
        console.error("Error initializing database:", error);
        showToast('Error', 'Failed to initialize database.', 'danger');
    });
});

const translations = {
    en: {
        language: "Language",
        heroTitle: "Find your next stay",
        heroSubtitle: "Search low prices on hotels, homes and much more...",
        search: "Search",
        filterBy: "Filter by",
        priceRange: "Price Range",
        starRating: "Star Rating",
        guestReviews: "Guest Reviews",
        amenities: "Amenities",
        sortByRecommended: "Recommended",
        sortByPriceAsc: "Price (low to high)",
        sortByPriceDesc: "Price (high to low)",
        sortByRating: "Rating",
        hotelsFound: (count) => `${count} hotels found`,
        excellent: "Excellent",
        veryGood: "Very Good",
        good: "Good"
    },
    fr: {
        language: "Langue",
        heroTitle: "Trouvez votre prochain séjour",
        heroSubtitle: "Recherchez des hôtels, des maisons et bien plus encore à bas prix...",
        search: "Rechercher",
        filterBy: "Filtrer par",
        priceRange: "Échelle de prix",
        starRating: "Classement par étoiles",
        guestReviews: "Avis des clients",
        amenities: "Équipements",
        sortByRecommended: "Recommandé",
        sortByPriceAsc: "Prix (croissant)",
        sortByPriceDesc: "Prix (décroissant)",
        sortByRating: "Classement",
        hotelsFound: (count) => `${count} hôtels trouvés`,
        excellent: "Excellent",
        veryGood: "Très bien",
        good: "Bien"
    },
    ar: {
        language: "لغة",
        heroTitle: "ابحث عن إقامتك التالية",
        heroSubtitle: "ابحث عن أسعار منخفضة للفنادق والمنازل وأكثر من ذلك بكثير...",
        search: "بحث",
        filterBy: "تصفية حسب",
        priceRange: "טווח מחירים",
        starRating: "تصنيف بالنجوم",
        guestReviews: "تقييمات النزلاء",
        amenities: "وسائل الراحة",
        sortByRecommended: "موصى به",
        sortByPriceAsc: "السعر (من الأقل إلى الأعلى)",
        sortByPriceDesc: "السعر (من الأعلى إلى الأقل)",
        sortByRating: "تقييم",
        hotelsFound: (count) => `تم العثور على ${count} فندق`,
        excellent: "ممتاز",
        veryGood: "جيد جدا",
        good: "جيد"
    }
};

let currentLanguage = 'en';

function changeLanguage(lang) {
    currentLanguage = lang;
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[lang][key]) {
            if (typeof translations[lang][key] === 'function') {
                // If you need to update dynamic text, handle it here
            } else {
                el.innerText = translations[lang][key];
            }
        }
    });
    // Re-render hotels to apply language changes if necessary
     renderHotels();
}

function getTranslation(key, ...args) {
    const translation = translations[currentLanguage][key];
    if (typeof translation === 'function') {
        return translation(...args);
    }
    return translation || key;
}


function setupEventListeners() {
    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    darkModeToggle.addEventListener('change', () => {
        document.body.setAttribute('data-bs-theme', darkModeToggle.checked ? 'dark' : 'light');
    });

    // Search Form
    const searchForm = document.getElementById('searchForm');
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        renderHotels();
    });

    // Filters
    document.getElementById('priceRange').addEventListener('input', handleFilterChange);
    document.getElementById('starRatingFilter').addEventListener('change', handleFilterChange);
    document.getElementById('reviewFilter').addEventListener('change', handleFilterChange);
    document.getElementById('amenitiesFilter').addEventListener('change', handleFilterChange);

    // Sorting
    document.getElementById('sortBy').addEventListener('change', renderHotels);

    // View Toggle
    document.getElementById('listViewBtn').addEventListener('click', () => toggleView('list'));
    document.getElementById('mapViewBtn').addEventListener('click', () => toggleView('map'));

    // Price range value display
    const priceRange = document.getElementById('priceRange');
    const priceValue = document.getElementById('priceValue');
    priceRange.addEventListener('input', () => {
        priceValue.textContent = `$${priceRange.value}`;
    });
}

function handleFilterChange() {
    renderHotels();
}

function setInitialValues() {
    // Set default check-in/out dates
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('checkin').value = today.toISOString().split('T')[0];
    document.getElementById('checkout').value = tomorrow.toISOString().split('T')[0];
}

async function renderHotels() {
    const hotels = await window.db.getAllHotels();
    const filteredHotels = filterAndSortHotels(hotels);

    const hotelListContainer = document.getElementById('hotel-list-container');
    hotelListContainer.innerHTML = ''; // Clear existing list

    if (filteredHotels.length === 0) {
        hotelListContainer.innerHTML = '<p>No hotels found matching your criteria.</p>';
    } else {
        filteredHotels.forEach(hotel => {
            hotelListContainer.appendChild(createHotelCard(hotel));
        });
    }

    // Update hotel count
    document.getElementById('hotelCount').textContent = getTranslation('hotelsFound', filteredHotels.length);

    // Update map view
    updateMapView(filteredHotels);
}

function filterAndSortHotels(hotels) {
    // Get filter values
    const destination = document.getElementById('destination').value.toLowerCase();
    const priceRange = document.getElementById('priceRange').value;

    const selectedRatings = Array.from(document.querySelectorAll('#starRatingFilter input:checked')).map(el => parseInt(el.value));
    const selectedReviews = Array.from(document.querySelectorAll('#reviewFilter input:checked')).map(el => el.value);
    const selectedAmenities = Array.from(document.querySelectorAll('#amenitiesFilter input:checked')).map(el => el.value);

    // Filter
    let filtered = hotels.filter(hotel => {
        // Destination
        if (destination && !hotel.location.toLowerCase().includes(destination) && !hotel.name.toLowerCase().includes(destination)) {
            return false;
        }
        // Price
        if (hotel.price > priceRange) {
            return false;
        }
        // Rating
        if (selectedRatings.length > 0 && !selectedRatings.includes(hotel.rating)) {
            return false;
        }
        // Reviews
        if (selectedReviews.length > 0 && !selectedReviews.includes(hotel.reviewText)) {
            return false;
        }
        // Amenities
        if (selectedAmenities.length > 0 && !selectedAmenities.every(a => hotel.amenities.includes(a))) {
            return false;
        }
        return true;
    });

    // Sort
    const sortBy = document.getElementById('sortBy').value;
    switch (sortBy) {
        case 'price_asc':
            filtered.sort((a, b) => a.price - b.price);
            break;
        case 'price_desc':
            filtered.sort((a, b) => b.price - a.price);
            break;
        case 'rating_desc':
            filtered.sort((a, b) => b.rating - a.rating);
            break;
    }

    return filtered;
}

function createHotelCard(hotel) {
    const card = document.createElement('div');
    card.className = 'card hotel-card mb-3';

    const reviewClass = hotel.reviewScore > 9 ? 'bg-success' : hotel.reviewScore > 8 ? 'bg-primary' : 'bg-info';

    card.innerHTML = `
        <div class="row g-0">
            <div class="col-md-4">
                <img src="${hotel.image}" class="img-fluid rounded-start" alt="${hotel.name}">
            </div>
            <div class="col-md-8">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="card-title">${hotel.name}</h5>
                        <div class="text-end">
                            <span class="badge ${reviewClass} text-white">${hotel.reviewScore}</span>
                            <small class="text-muted">${getTranslation(hotel.reviewText.toLowerCase().replace(' ', ''))}</small>
                        </div>
                    </div>
                    <p class="card-text"><small class="text-muted"><i class="fas fa-map-marker-alt"></i> ${hotel.location}</small></p>
                    <div class="d-flex justify-content-between align-items-center">
                         <div>
                            ${'<i class="fas fa-star text-warning"></i>'.repeat(hotel.rating)}
                            ${'<i class="far fa-star text-warning"></i>'.repeat(5 - hotel.rating)}
                        </div>
                        <div class="text-end">
                            <h4 class="mb-0">$${hotel.price}</h4>
                            <small class="text-muted">per night</small>
                        </div>
                    </div>
                     <p class="card-text mt-2">${hotel.description}</p>
                    <div class="amenities mt-2">
                        ${hotel.amenities.map(a => `<span class="badge bg-light text-dark me-1"><i class="fas fa-check"></i> ${a}</span>`).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    return card;
}

function updateFilterOptions() {
    // Star ratings
    const starFilterContainer = document.getElementById('starRatingFilter');
    starFilterContainer.innerHTML = [5, 4, 3, 2, 1].map(s => `
        <div class="form-check">
            <input class="form-check-input" type="checkbox" value="${s}" id="star${s}">
            <label class="form-check-label" for="star${s}">
                ${'<i class="fas fa-star text-warning"></i>'.repeat(s)}
            </label>
        </div>
    `).join('');

    // Reviews
    const reviewFilterContainer = document.getElementById('reviewFilter');
    reviewFilterContainer.innerHTML = ['Excellent', 'Very Good', 'Good'].map(r => `
        <div class="form-check">
            <input class="form-check-input" type="checkbox" value="${r}" id="review${r.replace(' ', '')}">
            <label class="form-check-label" for="review${r.replace(' ', '')}">${getTranslation(r.toLowerCase().replace(' ', ''))}</label>
        </div>
    `).join('');

    // Amenities
    const amenities = ['WiFi', 'Pool', 'Breakfast', 'Parking', 'Spa'];
    const amenitiesFilterContainer = document.getElementById('amenitiesFilter');
    amenitiesFilterContainer.innerHTML = amenities.map(a => `
        <div class="form-check">
            <input class="form-check-input" type="checkbox" value="${a}" id="amenity${a}">
            <label class="form-check-label" for="amenity${a}">${a}</label>
        </div>
    `).join('');
}


let map;
function initMapView() {
    if (!map) {
        map = L.map('map').setView([34.0522, -118.2437], 7); // Default to LA
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
}

function updateMapView(hotels) {
     if (map) {
        // Clear existing markers
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });

        // Add new markers - Geocoding would be needed for real addresses
        // For now, we'll use placeholder coordinates
        hotels.forEach((hotel, index) => {
            const lat = 34.0522 + (Math.random() - 0.5) * 0.1 * index;
            const lng = -118.2437 + (Math.random() - 0.5) * 0.1 * index;
            L.marker([lat, lng]).addTo(map)
                .bindPopup(`<b>${hotel.name}</b><br>$${hotel.price}/night`);
        });
    }
}

function toggleView(view) {
    const listView = document.getElementById('hotel-list-container');
    const mapView = document.getElementById('map-view-container');
    const listBtn = document.getElementById('listViewBtn');
    const mapBtn = document.getElementById('mapViewBtn');

    if (view === 'map') {
        listView.classList.add('d-none');
        mapView.classList.remove('d-none');
        listBtn.classList.remove('active');
        mapBtn.classList.add('active');
        initMapView();
        renderHotels(); // To update markers
    } else {
        mapView.classList.add('d-none');
        listView.classList.remove('d-none');
        mapBtn.classList.remove('active');
        listBtn.classList.add('active');
    }
}

// Toast Notification
function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('notificationToast');
    const toast = new bootstrap.Toast(toastEl);

    document.getElementById('toast-title').textContent = title;
    document.getElementById('toast-body').textContent = message;

    toastEl.classList.remove('bg-info', 'bg-success', 'bg-warning', 'bg-danger');
    toastEl.classList.add(`bg-${type}`, 'text-white');

    toast.show();
}

window.changeLanguage = changeLanguage;
