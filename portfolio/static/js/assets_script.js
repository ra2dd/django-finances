const table = document.querySelector('tbody');

const emptyRows = [];
const dataRows = [];
const index = 5;


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

typeButtons = [btnAll, btnCrypto, btnStock, btnCurrency];

btnAll.addEventListener('click', (e) => filterRowType('all', e));
btnCrypto.addEventListener('click', (e) => filterRowType('cryptocurrency', e));
btnStock.addEventListener('click', (e) => filterRowType('stock', e));
btnCurrency.addEventListener('click', (e) => filterRowType('currency', e));
btnEmptyValues.addEventListener('click', (e) => changeEmptyValuesVisibility(e));

function changeEmptyValuesVisibility(event) {
  emptyRowsVisible = !emptyRowsVisible;
  
  if (emptyRowsVisible == false) {
    event.target.setAttribute('class', 'active');
  } else {
    event.target.removeAttribute('class');
  }

  filterRowType(activeFilter, false);
}

function filterRowType(type, event) {
  emptyTable();
  activeFilter = type;

  if (event != false){
    for (const button of typeButtons) {
      if (button.getAttribute('class') == 'active') {
        button.removeAttribute('class');
      }
    }
    event.target.setAttribute('class', 'active');
  }

  if (type == 'all') {
    appendDataRows();
  } 
  else {
    for (const row of dataRows) {
      if (row.children[index+1].childNodes[0].data == type) {
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
        if (row.children[index+1].childNodes[0].data == type) {
          table.appendChild(row);
        }
      }
    }
  }
}
        