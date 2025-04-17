const fs = require('fs');
const https = require('https');
const path = require('path');

const FIREBASE_VERSION = '10.8.0';
const FIREBASE_FILES = [
  'firebase-app',
  'firebase-auth',
  'firebase-firestore'
];

const downloadFile = (url, dest) => {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
};

async function downloadFirebaseFiles() {
  for (const file of FIREBASE_FILES) {
    const url = `https://www.gstatic.com/firebasejs/${FIREBASE_VERSION}/${file}.js`;
    const dest = path.join(__dirname, `${file}.js`);
    console.log(`Downloading ${url} to ${dest}`);
    try {
      await downloadFile(url, dest);
      console.log(`Successfully downloaded ${file}.js`);
    } catch (error) {
      console.error(`Error downloading ${file}.js:`, error);
    }
  }
}

downloadFirebaseFiles(); 