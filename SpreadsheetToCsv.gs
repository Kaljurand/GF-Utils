var settings = {
  "key": '0Aprlzd4hAZrEdGVmYnBwZWdyVkUwQ0RBZE5BSXB1OEE',
  "nl": '\n',
  "sep": ','
};

function doGet() {
  return ContentService.createTextOutput(convertSheetToCsv_(settings.key));
}

// We have two metacharacters: " and ,
// Iff the cell contains either of them, then its value is wrapped into quotes.
// Iff the cell contains quotes (prior to wrapping), then the quotes are escaped
// by doubling them.
function convertSheetToCsv_(id) {
  var csv = "";
  try {
    var ss = SpreadsheetApp.openById(id);
    var sheet = ss.getSheets()[0];
    var data = sheet.getDataRange().getValues();

    for (var row = 0; row < data.length; row++) {
      for (var col = 0; col < data[row].length; col++) {
        var cell = data[row][col].toString();
        cell = cell.replace(/"/g, '""');
        if (cell.indexOf(settings.sep) != -1 || cell.indexOf('"') != -1) {
          cell = '"' + cell + '"';
        }
        data[row][col] = cell;
      }
      csv += data[row].join(settings.sep) + settings.nl;
    }
  } catch(err) {
    csv = err;
  } finally {
    return csv;
  }
}
