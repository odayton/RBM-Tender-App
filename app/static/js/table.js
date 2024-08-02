document.addEventListener("DOMContentLoaded", function () {
    var tableHeaders = document.querySelectorAll(".table-resizable th");
    var startX, startWidth;

    tableHeaders.forEach(function (th, index) {
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

        th.addEventListener("click", function () {
            sortTable(index);
        });

        function resizeColumn(event) {
            var newWidth = startWidth + (event.pageX - startX);
            th.style.width = newWidth + "px";
        }
        
        function stopResize() {
            document.removeEventListener("mousemove", resizeColumn);
            document.removeEventListener("mouseup", stopResize);
        }
    });

    // Store the current sort direction for each column
    var sortDirections = Array(tableHeaders.length).fill(null);

    function sortTable(n) {
        var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
        table = document.querySelector(".table-resizable");
        switching = true;
        
        // Toggle the sort direction for the clicked column
        if (sortDirections[n] === "asc") {
            dir = "desc";
        } else {
            dir = "asc";
        }
        sortDirections[n] = dir;
        
        // Remove sort indicators from all headers
        tableHeaders.forEach(function (header) {
            header.classList.remove("sort-asc", "sort-desc");
        });
        // Add the sort indicator to the clicked header
        tableHeaders[n].classList.add("sort-" + dir);

        while (switching) {
            switching = false;
            rows = table.rows;
            for (i = 1; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = rows[i].getElementsByTagName("TD")[n];
                y = rows[i + 1].getElementsByTagName("TD")[n];
                if (dir == "asc") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                } else if (dir == "desc") {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount ++; 
            } else {
                if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
    }
});
