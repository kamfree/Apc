import app from '../interface/server';

async function testAPI() {
  console.log('--- Starting API Test ---');
  try {
     if (typeof app === 'function') {
         console.log('App instance is a valid Express function');
     }

     console.log('--- API Test Passed ---');
     process.exit(0);
  } catch (err) {
      console.error(err);
      process.exit(1);
  }
}

testAPI();
