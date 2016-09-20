export function objectType(obj) {
  return Object.prototype.toString.call(obj).slice(8, -1);
}

export function contains(array, x) {
  return (array.find(el => (el === x)) !== undefined);
}

export function $try(func) {
  try {
    return func();
  } catch (e) {
    return null;
  }
}

export function reformatDatetime(dtStr) {
  return new Date(dtStr).toString();
}

export function downloadCSV(data, filename) {
  const a = document.createElement('a');
  const blob = new Blob(data, { type: 'application/octet-stream' });
  a.href = window.URL.createObjectURL(blob);
  a.download = filename;
  a.click();
}
