// /static/js/table.js

document.addEventListener('DOMContentLoaded', () => {

    // --- Resizable Columns Logic ---
    const resizableTables = document.querySelectorAll('table.resizable');
    resizableTables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach(header => {
            const grip = document.createElement('div');
            grip.style.position = 'absolute';
            grip.style.right = '0';
            grip.style.top = '0';
            grip.style.bottom = '0';
            grip.style.width = '5px';
            grip.style.cursor = 'col-resize';
            grip.style.userSelect = 'none';
            header.style.position = 'relative'; // Necessary for absolute positioning of grip
            header.appendChild(grip);

            grip.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const startX = e.pageX;
                const startWidth = header.offsetWidth;
                
                const onMouseMove = (moveEvent) => {
                    const newWidth = startWidth + (moveEvent.pageX - startX);
                    if (newWidth > 40) { // Set a minimum width
                        header.style.width = `${newWidth}px`;
                    }
                };
                
                const onMouseUp = () => {
                    document.removeEventListener('mousemove', onMouseMove);
                    document.removeEventListener('mouseup', onMouseUp);
                };
                
                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            });
        });
    });

    // --- Sortable Rows Logic ---
    let draggedRow = null;
    const sortableTables = document.querySelectorAll('table.sortable-table tbody');
    sortableTables.forEach(tbody => {
        const rows = tbody.querySelectorAll('tr');
        rows.forEach(row => {
            row.setAttribute('draggable', 'true');
            
            row.addEventListener('dragstart', (e) => {
                draggedRow = row;
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', row.innerHTML); // For Firefox compatibility
                row.classList.add('dragging');
            });

            row.addEventListener('dragend', (e) => {
                draggedRow.classList.remove('dragging');
                draggedRow = null;
            });
        });
        
        tbody.addEventListener('dragover', (e) => {
            e.preventDefault();
            const targetRow = e.target.closest('tr');
            if (targetRow && targetRow !== draggedRow) {
                // Determine if dragging above or below the target row
                const rect = targetRow.getBoundingClientRect();
                const nextSibling = (e.clientY - rect.top) > (rect.height / 2) ? targetRow.nextSibling : targetRow;
                tbody.insertBefore(draggedRow, nextSibling);
            }
        });

        tbody.addEventListener('drop', (e) => {
            e.preventDefault();
            // The actual re-ordering happens in 'dragover', so drop is just for cleanup.
            // You might add a server-side call here to save the new order.
        });
    });
});