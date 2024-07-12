document.addEventListener("DOMContentLoaded", function () {
    var tableHeaders = document.querySelectorAll(".table-resizable th");
    var startX, startWidth;

    tableHeaders.forEach(function (th) {
        // Create a div element for resizing handle
        var resizer = document.createElement("div");
        resizer.className = "resizer";
        th.appendChild(resizer);
        
        resizer.addEventListener("mousedown", function (event) {
            startX = event.pageX;
            startWidth = th.offsetWidth;

            document.addEventListener("mousemove", resizeColumn);
            document.addEventListener("mouseup", stopResize);
        });

        function resizeTable() {
            // Get the table element
            var table = document.querySelector('.table');
          
            // Calculate available width for the table
            var availableWidth = window.innerWidth 
                                 - document.getElementById('sidebar').offsetWidth; // Subtract sidebar width
          
            // Set the table width to the available space
            table.style.width = availableWidth + 'px';
          
            // Recalculate column widths based on the new table width (optional)
            var totalColumns = table.querySelectorAll('th').length;
            var columnWidth = Math.floor(availableWidth / totalColumns);
            table.querySelectorAll('th').forEach(function(th) {
              th.style.width = columnWidth + 'px';
            });
          }
        
        function resizeColumn(event) {
            var newWidth = startWidth + (event.pageX - startX);
            th.style.width = newWidth + "px";
        }
        
        function stopResize() {
            document.removeEventListener("mousemove", resizeColumn);
            document.removeEventListener("mouseup", stopResize);
        }
    });
});
