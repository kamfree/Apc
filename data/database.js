// data/database.js

const DB_NAME = 'HotelBladiDB';
const DB_VERSION = 1;
const STORES = {
    HOTELS: 'hotels',
    BOOKINGS: 'bookings',
    USERS: 'users'
};

let db;

function openDatabase() {
    return new Promise((resolve, reject) => {
        if (db) {
            return resolve(db);
        }

        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = (event) => {
            console.error('Database error:', event.target.errorCode);
            reject('Database error: ' + event.target.errorCode);
        };

        request.onupgradeneeded = (event) => {
            db = event.target.result;
            if (!db.objectStoreNames.contains(STORES.HOTELS)) {
                const hotelStore = db.createObjectStore(STORES.HOTELS, { keyPath: 'id', autoIncrement: true });
                hotelStore.createIndex('name', 'name', { unique: false });
                hotelStore.createIndex('location', 'location', { unique: false });
                hotelStore.createIndex('rating', 'rating', { unique: false });
                hotelStore.createIndex('price', 'price', { unique: false });
            }
            if (!db.objectStoreNames.contains(STORES.BOOKINGS)) {
                db.createObjectStore(STORES.BOOKINGS, { keyPath: 'id', autoIncrement: true });
            }
            if (!db.objectStoreNames.contains(STORES.USERS)) {
                db.createObjectStore(STORES.USERS, { keyPath: 'id', autoIncrement: true });
            }
        };

        request.onsuccess = (event) => {
            db = event.target.result;
            db.onversionchange = () => {
                db.close();
                alert("A new version of the page is ready. Please reload!");
            };
            populateInitialData().then(() => resolve(db));
        };
    });
}

async function populateInitialData() {
    await openDatabase();
    const transaction = db.transaction(STORES.HOTELS, 'readonly');
    const store = transaction.objectStore(STORES.HOTELS);
    const countRequest = store.count();

    return new Promise((resolve) => {
        countRequest.onsuccess = () => {
            if (countRequest.result === 0) {
                const initialHotels = [
                    { name: 'Grand Hyatt', location: 'New York', rating: 5, reviewScore: 9.2, reviewText: 'Excellent', price: 350, image: 'https://picsum.photos/seed/h1/400/300', description: 'A luxurious hotel in the heart of the city.', amenities: ['WiFi', 'Pool', 'Spa'], tags: ['luxury', 'business'] },
                    { name: 'Hilton Garden Inn', location: 'Los Angeles', rating: 4, reviewScore: 8.5, reviewText: 'Very Good', price: 200, image: 'https://picsum.photos/seed/h2/400/300', description: 'Comfort and convenience for all travelers.', amenities: ['WiFi', 'Breakfast', 'Parking'], tags: ['family', 'value'] },
                    { name: 'Marriott Marquis', location: 'Chicago', rating: 4, reviewScore: 8.8, reviewText: 'Very Good', price: 280, image: 'https://picsum.photos/seed/h3/400/300', description: 'Modern hotel with stunning city views.', amenities: ['WiFi', 'Pool', 'Breakfast'], tags: ['modern', 'views'] },
                    { name: 'Holiday Inn Express', location: 'Miami', rating: 3, reviewScore: 7.9, reviewText: 'Good', price: 150, image: 'https://picsum.photos/seed/h4/400/300', description: 'A great choice for a budget-friendly stay.', amenities: ['WiFi', 'Breakfast'], tags: ['budget', 'beach'] }
                ];

                const addTransaction = db.transaction(STORES.HOTELS, 'readwrite');
                const addStore = addTransaction.objectStore(STORES.HOTELS);
                initialHotels.forEach(hotel => {
                    // Manually set an ID if it's not auto-incrementing as expected
                    if (!hotel.id) {
                        // This part is tricky as we can't easily guarantee uniqueness without auto-increment
                        // For this example, we'll let auto-increment handle it, but this is a point of caution.
                    }
                    addStore.add(hotel);
                });
                addTransaction.oncomplete = () => resolve();
                addTransaction.onerror = () => reject(addTransaction.error);

            } else {
                resolve();
            }
        };
        countRequest.onerror = () => reject(countRequest.error);
    });
}


// CRUD operations for hotels
async function addHotel(hotel) {
    await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORES.HOTELS], 'readwrite');
        const store = transaction.objectStore(STORES.HOTELS);
        const request = store.add(hotel);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function getAllHotels() {
    await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORES.HOTELS], 'readonly');
        const store = transaction.objectStore(STORES.HOTELS);
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function getHotelById(id) {
    await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORES.HOTELS], 'readonly');
        const store = transaction.objectStore(STORES.HOTELS);
        const request = store.get(id);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function updateHotel(hotel) {
    await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORES.HOTELS], 'readwrite');
        const store = transaction.objectStore(STORES.HOTELS);
        const request = store.put(hotel);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function deleteHotel(id) {
    await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORES.HOTELS], 'readwrite');
        const store = transaction.objectStore(STORES.HOTELS);
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

// Expose functions to global scope to be accessible from other scripts
window.db = {
    openDatabase,
    addHotel,
    getAllHotels,
    getHotelById,
    updateHotel,
    deleteHotel,
};
