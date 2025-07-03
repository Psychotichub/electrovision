require('dotenv').config();

const express = require('express');
const cors = require('cors');

const app = express();

console.log('🚀 Starting ElectroVision AI Backend Server...');

process.on('uncaughtException', err => {
  console.error('❌ Uncaught Exception:', err);
  process.exit(1);
});
process.on('unhandledRejection', err => {
  console.error('❌ Unhandled Rejection:', err);
  process.exit(1);
});

app.use(cors());
app.use(express.json());

// Basic health check route
app.get('/', (req, res) => {
  res.json({ 
    message: 'ElectroVision AI Backend is running!',
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Load upload route with error handling
try {
  console.log('📁 Loading upload route...');
  const uploadRoute = require('./routes/upload');
  app.use('/upload', uploadRoute);
  console.log('✅ Upload route loaded successfully');
} catch (error) {
  console.error('❌ Error loading upload route:', error.message);
  console.log('⚠️  Server will continue without upload functionality');
}

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}`);
  console.log(`🌐 Health check: http://localhost:${PORT}/`);
  console.log(`📤 Upload endpoint: http://localhost:${PORT}/upload`);
  console.log('🔄 Server is ready and waiting for requests...');
});

// Keep the server alive
server.on('error', (err) => {
  console.error('❌ Server error:', err);
});

// Graceful shutdown handling
process.on('SIGTERM', () => {
  console.log('🛑 Received SIGTERM, shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('🛑 Received SIGINT, shutting down gracefully...');
  server.close(() => {
    console.log('✅ Server closed');
    process.exit(0);
  });
});
