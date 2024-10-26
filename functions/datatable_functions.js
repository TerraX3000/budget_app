
function render_input_cell(data, type, row, meta) {
    if (type === 'export') {
        return data
    }
    return `<input type="number" class="ai-input ai-border ai-round ai-dark-gray ai-text-white"  type="number" value="${data}" />`;
}


function on_click_submit_table_values() {
    dt = window.publicJsFunctions.getDataTableApi();
    // Get the column headers
    const headers = dt.columns(':visible').header().toArray().map(header => header.innerText.trim());

    // Initialize an array to hold the row dictionaries
    const tableData = [];

    // Iterate over each row in the DataTable
    dt.rows({ filter: 'applied' }).every(function (rowIdx) {
        // Initialize a dictionary for the current row
        const rowData = {};

        // Loop through each column and get cell data for the current row
        headers.forEach((header, colIdx) => {
            const cellNode = dt.cell(rowIdx, colIdx).node();
            let cellData = dt.cell(rowIdx, colIdx).data();

            // If the cell has an input field, get its value
            const inputField = cellNode.querySelector('input.ai-input');
            if (inputField) {
                cellData = inputField.value;
                // Check if the input type is "number" and convert value to number
                if (inputField.type === 'number') {
                    cellData = parseFloat(cellData);
                }
            }

            // Assign cell data to the header in the current row dictionary
            rowData[header] = cellData;
        });

        // Add the row dictionary to the array
        tableData.push(rowData);
    });
    // Optionally, pass the data to a callback or other handler
    window.publicJsFunctions.setComponentValue({ "allValues": tableData });
}