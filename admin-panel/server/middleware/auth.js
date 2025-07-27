const jwt = require('jsonwebtoken');

function auth(req, res, next) {
  const token = req.header('x-auth-token');

  // Check for token
  if (!token) {
    return res.status(401).json({ msg: 'No token, authorization denied' });
  }

  try {
    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    // Add user from payload
    req.user = decoded;
    next();
  } catch (e) {
    res.status(400).json({ msg: 'Token is not valid' });
  }
}

function adminAuth(req, res, next) {
    auth(req, res, () => {
        if (req.user.role === 'Admin' || req.user.role === 'Super Admin') {
            next();
        } else {
            res.status(401).json({ msg: 'Admin authorization denied' });
        }
    });
}

function superAdminAuth(req, res, next) {
    auth(req, res, () => {
        if (req.user.role === 'Super Admin') {
            next();
        } else {
            res.status(401).json({ msg: 'Super Admin authorization denied' });
        }
    });
}

module.exports = { auth, adminAuth, superAdminAuth };
