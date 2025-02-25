import pandas as pd
import json

# Load CSV file
file_path = r'D:\三麟印刷\ELog_Stastic.csv'  
data = pd.read_csv(file_path)

# Convert date format
data['Date'] = pd.to_datetime(data['Date'])

# Transform data
data_melted = data.melt(id_vars='Date', var_name='Device Name', value_name='Energy Consumption (kWh)')
daily_consumption = data_melted.groupby(['Date', 'Device Name'])['Energy Consumption (kWh)'].sum().reset_index()

# Set up JSON data
devices_data = {
    device: daily_consumption[daily_consumption['Device Name'] == device]
    .assign(Date=daily_consumption[daily_consumption['Device Name'] == device]['Date'].dt.strftime('%Y-%m-%d'))
    .to_dict(orient='records')
    for device in daily_consumption['Device Name'].unique()
}

# Ensure JSON formatting is correct
devices_json = json.dumps(devices_data, ensure_ascii=False, indent=4)

# HTML content
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Device Power Consumption Trend</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; }}
        .container {{ margin: 20px; padding: 20px; text-align: center; }}
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .grid-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            background: linear-gradient(to bottom, #ffffff, #f0f0f0);
            border-radius: 8px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .alert {{ 
            color: red; font-weight: bold; background-color: rgba(255, 0, 0, 0.1); 
            padding: 5px; border-radius: 5px; margin-top: 10px; 
        }}
        .threshold {{ font-size: 18px; font-weight: bold; }}
        input[type="number"], input[type="range"] {{ width: 120px; margin-left: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: #2C3E50;">📊 Device Power Consumption Trend</h2>
        <h4 class="threshold">🛠 Select Device & Set Consumption Threshold:</h4>
        <div id="threshold-container" class="grid-container"></div>
        <div id="chart" style="height: 500px;"></div>
        <div id="alert-container"></div>
    </div>
    <script>
        let devices = JSON.parse(`{devices_json}`);

        console.log("Device Data:", devices);

        if (!devices || Object.keys(devices).length === 0) {{
            document.getElementById("threshold-container").innerHTML = "<p style='color:red;'>⚠️ No available device data. Please check the data source!</p>";
        }}

        const thresholdContainer = document.getElementById("threshold-container");
        const alertContainer = document.getElementById("alert-container");
        const chartDiv = document.getElementById("chart");

        let layout = {{
            title: '📈 Daily Device Power Consumption Trend (Unit: kWh)',
            xaxis: {{ title: '📅 Date', tickangle: -45 }},
            yaxis: {{ title: '🔋 Power Consumption (kWh)' }},
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#eef2f7',
            font: {{ family: "Arial", size: 14, color: "#333333" }},
        }};

        const colors = ['#FF5733', '#33FF57', '#5733FF', '#FFD700', '#FF33A1', '#A133FF', '#33A1FF', '#FF8C33', '#33FFA1', '#A1FF33'];

        // Create device selection section
        for (let device in devices) {{
            const deviceContainer = document.createElement("div");
            deviceContainer.classList.add("grid-item");
            deviceContainer.innerHTML = `
                <input type="checkbox" id="toggle-${{device}}">
                <label for="toggle-${{device}}">${{device}}</label>
                <input type="number" id="threshold-${{device}}" value="1200" min="0" max="2000" step="1" oninput="syncSlider('${{device}}')">
                <input type="range" id="slider-${{device}}" value="1200" min="0" max="2000" step="1" oninput="syncNumber('${{device}}')">
            `;
            thresholdContainer.appendChild(deviceContainer);
        }}

        function syncSlider(device) {{
            document.getElementById("slider-" + device).value = document.getElementById("threshold-" + device).value;
            updateChart();
        }}

        function syncNumber(device) {{
            document.getElementById("threshold-" + device).value = document.getElementById("slider-" + device).value;
            updateChart();
        }}

        function updateChart() {{
            let traces = [];
            let colorIndex = 0;

            for (let device in devices) {{
                const checkbox = document.getElementById("toggle-" + device);
                const numberInput = document.getElementById("threshold-" + device);

                if (checkbox.checked) {{
                    let data = devices[device];

                    traces.push({{
                        x: data.map(d => d["Date"]),
                        y: data.map(d => d["Energy Consumption (kWh)"]),
                        mode: 'lines',
                        name: device,
                        line: {{ color: colors[colorIndex % colors.length], width: 3, shape: 'spline' }}
                    }});

                    let threshold = parseFloat(numberInput.value);
                    traces.push({{
                        x: data.map(d => d["Date"]),
                        y: Array(data.length).fill(threshold),
                        mode: 'lines',
                        name: device + " Threshold Line",
                        line: {{ color: colors[colorIndex % colors.length], dash: 'dot', width: 2 }}
                    }});

                    colorIndex++;
                }}
            }}

            Plotly.newPlot(chartDiv, traces, layout);
            updateAlerts();
        }}

        function updateAlerts() {{
            alertContainer.innerHTML = "";  

            for (let device in devices) {{
                const checkbox = document.getElementById("toggle-" + device);
                const numberInput = document.getElementById("threshold-" + device);

                if (!checkbox.checked) {{
                    continue;
                }}

                const threshold = parseFloat(numberInput.value);
                const deviceData = devices[device];

                let exceedDates = deviceData
                    .filter(d => parseFloat(d["Energy Consumption (kWh)"]) > threshold)
                    .map(d => d["Date"]);

                if (exceedDates.length > 0) {{
                    let alertMessage = document.createElement("p");
                    alertMessage.className = "alert fade-in";
                    alertMessage.textContent = `⚠️ Alert: ${{device}} exceeded the set range! Exceeded dates: ${{exceedDates.join(", ")}}`;
                    alertContainer.appendChild(alertMessage);
                }}
            }}
        }}

        updateChart();
    </script>
</body>
</html>"""

output_path = r'D:\Python Data\static_power_consumption_with_alerts_left_aligned.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML file successfully saved to: {output_path}")
