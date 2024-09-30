document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('stepThrough').addEventListener('click', stepThrough);
    document.getElementById('runToConvergence').addEventListener('click', runToConvergence);
    document.getElementById('generateNewDataset').addEventListener('click', generateNewDataset);
    document.getElementById('resetAlgorithm').addEventListener('click', resetAlgorithm);
});

let currStep = 0
let total = 0
let manPoints = []

function firstPlot(){
    // const numPoints = 30
    // const url = `/first?numPoints=${numPoints}&t=${new Date().getTime()}`;

    // const img = document.getElementById('visualization');
    // img.src = url;
    // img.style.display = 'block'; // Show the image
    const numPoints = 30;
    const url = `/first?numPoints=${numPoints}&t=${new Date().getTime()}`;
    const img = document.getElementById('visualization');
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.blob();
        })
        .then(blob => {
            const objectURL = URL.createObjectURL(blob);
            img.src = objectURL;
            img.style.display = 'block';
        })
        .catch(error => {
            console.error('Error in firstPlot:', error);
        });
}

function updateVisualization() {
    const method = document.getElementById('method').value;
    if (method === 'manual'){
        const canvas = document.getElementById('plotly-div');
        canvas.style.display = 'none';
    }
    const img = document.getElementById('visualization');
    
    // Add a timestamp to the URL to prevent caching
    const timestamp = new Date().getTime();
    img.src = `/getsnap?step_count=${currStep}&t=${timestamp}`;
    
    img.style.display = 'block'; // Show the image
    currStep++; // Increment the current step after updating the image
}

function stepThrough() {
    if (currStep == 0) {
        const numClusters = document.getElementById('numClusters').value;
        const method = document.getElementById('method').value;
        let url;
        
        if (method === 'manual') {
            const encodedPoints = encodeURIComponent(JSON.stringify(manPoints));
            url = `/manually?k=${numClusters}&manual_points=${encodedPoints}`;
        } else {
            url = `/execute?k=${numClusters}&first_method=${method}`;
        }
        
        fetch(url)
            .then(response => response.text())
            //.then(response => response.json())
            .then(data => {
                total = parseInt(data, 10);
                //total = data.step_count
                if (isNaN(total)) {
                    console.error("Failed to retrieve total steps from the server.");
                    return;
                }
                updateVisualization();
            })
            .catch(error => console.error("Error during initialization:", error));
    } else {
        if (currStep >= total) {
            alert("KMeans has converged.");
            return;
        }
        updateVisualization();
    }
}

function runToConvergence() {
    // Implement functionality to complete the algorithm
    if (currStep == 0) {
        const numClusters = document.getElementById('numClusters').value;
        const method = document.getElementById('method').value;
        
        if(method === 'manual') {
            const encodedPoints = encodeURIComponent(JSON.stringify(manPoints));
            const url = `/manually?k=${numClusters}&man_points=${encodedPoints}`;

            // Make an AJAX request to get the total steps from the server
        fetch(url)
            .then(response => response.json())
            .then(data => {
                //total = parseInt(data, 10);
                total = data.step_count
                if (isNaN(total)) {
                    console.error("Failed to retrieve total steps from the server.");
                    return;
                }
                // Start the visualization process
                currStep = total;
                updateVisualization();
            })
            .catch(error => console.error("Error during initialization:", error));
        }else{
            // Create the URL for the initial generation request
            const url = `/execute?k=${numClusters}&first_method=${method}`;
        
            // Make an AJAX request to get the total steps from the server
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    //total = parseInt(data, 10);    
                    total = data.step_count
                    if (isNaN(total)) {
                        console.error("Failed to retrieve total steps from the server.");
                        return;
                    }
                    // Start the visualization process
                    currStep = total;
                    updateVisualization();
                })
                .catch(error => console.error("Error during initialization:", error));
        }
    } else {
        // Check if we have reached the total steps
        if (currStep >= total) {
            alert("KMeans has converged.");
            return; // Stop if we've reached the end
        }
        
        // Show the next step visualization
        currStep = total;
        updateVisualization();
    }
}

function generateNewDataset() {

    const numPoints = 30
    const url = `/newdata?numPoints=${numPoints}&t=${new Date().getTime()}`;

    currStep = 0;
    total = 0;
    manPoints = [];
    // Reset the dropdown menu to "Select the Initialization Method"
    document.getElementById('method').selectedIndex = 0;

    const img = document.getElementById('visualization');
    img.src = url;
    img.style.display = 'block'; // Show the image
}

function resetAlgorithm() {
    // Reset necessary variables and UI components
    const url = `/resetplot`;

    const img = document.getElementById('visualization');
    img.src = url;
    img.style.display = 'block'; // Show the image
    currStep = 0;
    total = 0;
    manPoints = [];

    // Reset the dropdown menu to "Select the Initialization Method"
    document.getElementById('method').selectedIndex = 0;
}


//manual

document.getElementById('method').addEventListener('change', function () {
    const selectedMethod = this.value;
    const canvas = document.getElementById('plotly-div');
    const img = document.getElementById('visualization');

    if (selectedMethod === 'manual') {
        img.style.display = 'none';
        canvas.style.display = 'block';

        // Request Ajax for tne current Data points
        fetch('/getmanpoints')
            .then(response => response.json())
            .then(points => {
                manSelection(points);
            })
        
    } else {
        canvas.style.display = 'none';
        img.style.display = 'block';
    }
});

function manSelection(initialData) {
    const numClusters = parseInt(document.getElementById('numClusters').value, 10);

    const trace = {
        x: initialData.map(point => point[0]),
        y: initialData.map(point => point[1]),
        mode: 'markers',
        type: 'scatter',
        marker: {color:'blue'}, // initial points in blue
        name: 'Data Points',
        showlegend: false
    };

    const layout = {
        title: 'Select k Points',
        xaxis: { title: 'X'},
        yaxis: {title: 'Y'},
        dragmode: 'select',
    };

    Plotly.newPlot('plotly-div', [trace], layout);

    const plotlyDiv = document.getElementById('plotly-div');

    plotlyDiv.on('plotly_click', function(data) {
        if(manPoints.length < numClusters){
            const x = data.points[0].x;
            const y = data.points[0].y;
            manPoints.push({ x, y });
            
            const newTrace = {
                x: manPoints.map(point => point.x),
                y: manPoints.map(point => point.y),
                mode: 'markers',
                marker: {color: 'red', size: 10, symbol: 'x'}, // Selected points in red with a border
                type: 'scatter',
                name: 'Selected Points',
                hoverinfo: 'text',
                showlegend: true
            };

            Plotly.addTraces(plotlyDiv, newTrace); // Add the new trace with the selected points

            if (manPoints.length === numClusters){
                console.log('Selected Points:', selectedPoints);
            }
        } else{
            alert('You have selected all k points. Run KMeans Algorithm');
        }
    });
}


// Automatically generate visualization on page load
window.onload = function() {
    firstPlot();
};
