const table = document.querySelector('tbody');

const emptyRows = [];
const dataRows = [];
const index = 4;


function getRowValue(row) {
  return Number(row.children[index].childNodes[0].data);
}

function fetchAndSortData() {
  for (const row of table.children) {
    if (row.children[index].childNodes[0] == undefined) {
      emptyRows.push(row);
    }
    else {
      dataRows.push(row);
      // console.log(row.children[index].childNodes[0].data);
    }
  }
  
  dataRows.sort((a, b) => {
    if (getRowValue(a) < getRowValue(b)) {
      return 1;
    } else {
      return -1;
    }
  });
}

function emptyTable() {
  while(table.firstChild) {
    table.firstChild.remove();
  }
}

function appendDataRows() {
  for (const row of dataRows) {
    table.appendChild(row);
  }
}

function appendEmptyRows() {
  for (const row of emptyRows) {
    table.appendChild(row);
  }
}

fetchAndSortData();
emptyTable();
appendDataRows();
appendEmptyRows();

let emptyRowsVisible = true;
let activeFilter = 'all';

const btnAll = document.getElementById('btn-all');
const btnCrypto = document.getElementById('btn-crypto');
const btnStock = document.getElementById('btn-stock');
const btnCurrency = document.getElementById('btn-currency');
const btnEmptyValues = document.getElementById('btn-empty-values');

btnAll.addEventListener('click', () => filterRowType('all'));
btnCrypto.addEventListener('click', () => filterRowType('cryptocurrency'));
btnStock.addEventListener('click', () => filterRowType('stock'));
btnCurrency.addEventListener('click', () => filterRowType('currency'));
btnEmptyValues.addEventListener('click', () => changeEmptyValuesVisibility())

function changeEmptyValuesVisibility() {
  emptyRowsVisible = !emptyRowsVisible;
  filterRowType(activeFilter);
}

function filterRowType(type) {
  emptyTable();
  activeFilter = type

  if (type == 'all') {
    appendDataRows();
  } 
  else {
    for (const row of dataRows) {
      if (row.children[index-1].childNodes[0].data == type) {
        table.appendChild(row);
      }
    }    
  }

  if (emptyRowsVisible == true) {
    if (type == 'all') {
      appendEmptyRows();
    } 
    else {
      for (const row of emptyRows) {
        if (row.children[index-1].childNodes[0].data == type) {
          table.appendChild(row);
        }
      }
    }
  }
}
        