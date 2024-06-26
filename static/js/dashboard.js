fetch('/dashboard_data')
    .then(response => response.json())
    .then(data => {
        // Extract pump names and counts for most selected pumps
        const pumpNamesMost = data.mostSelected.map(pump => pump.name);
        const pumpCountsMost = data.mostSelected.map(pump => pump.count);

        // Extract pump names and counts for least selected pumps
        const pumpNamesLeast = data.leastSelected.map(pump => pump.name);
        const pumpCountsLeast = data.leastSelected.map(pump => pump.count);

        // Create a horizontal bar chart for most selected pumps using Plotly
        const trace1 = {
            y: pumpNamesMost,
            x: pumpCountsMost,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: 'rgba(50, 171, 96, 0.6)',
                width: 0.3
            }
        };

        const layout1 = {
            title: 'Top 10 Most Selected Pumps',
            yaxis: {
                title: 'Pump Name'
            },
            xaxis: {
                title: 'Selection Count'
            },
            margin: {
                l: 200
            }
        };

        Plotly.newPlot('graph1', [trace1], layout1);

        // Create a horizontal bar chart for least selected pumps using Plotly
        const trace2 = {
            y: pumpNamesLeast,
            x: pumpCountsLeast,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: 'rgba(171, 50, 96, 0.6)',
                width: 0.3
            }
        };

        const layout2 = {
            title: 'Top 10 Least Selected Pumps',
            yaxis: {
                title: 'Pump Name'
            },
            xaxis: {
                title: 'Selection Count'
            },
            margin: {
                l: 200
            }
        };

        Plotly.newPlot('graph2', [trace2], layout2);
    })
    .catch(error => console.error('Error fetching dashboard data:', error));
