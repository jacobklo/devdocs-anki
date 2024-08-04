/*
First, go to devdocs.io and make whatever documentation offline.
The offline docs is saved in indexDB, which this script will download and save it as a json file.

Open Chrome dev tools, replace the language you want, and copy this script into the console.

*/


function saveTextToFile(text, filename) {
  const blob = new Blob([text], { type: 'text/plain' });
  const anchor = document.createElement('a');
  anchor.href = URL.createObjectURL(blob);
  anchor.download = filename;
  anchor.click();
}

function downloadIndexexDB(lang='react') {
  let resultData = {};
  let request = indexedDB.open('docs');
  request.onsuccess = (event) => {
    let db = event.target.result;
    let transaction = db.transaction([lang], 'readonly');
    let objectStore = transaction.objectStore(lang);
    let keyRequest = objectStore.getAllKeys();
    
    keyRequest.onsuccess = () => {
      let keys = keyRequest.result;
      keys.forEach(key => {
        let valueRequest = objectStore.get(key);
        valueRequest.onsuccess = () => {
          resultData[key] = valueRequest.result;
        };
      });
    };
  };

  return JSON.stringify(resultData, null, 2);
}


result_json = downloadIndexexDB('react')
saveTextToFile(result_json, 'react.json')