import pandas as pd
import json

# 讀取 CSV 檔案
file_path = 'ELog_Stastic.csv'
data = pd.read_csv(file_path)

# 轉換日期格式
data['Date'] = pd.to_datetime(data['Date'])

# 轉換資料格式
data_melted = data.melt(id_vars='Date', var_name='Device Name', value_name='Energy Consumption (kWh)')
daily_consumption = data_melted.groupby(['Date', 'Device Name'])['Energy Consumption (kWh)'].sum().reset_index()

# 產生 JSON
devices_data = {
    device: daily_consumption[daily_consumption['Device Name'] == device]
    .assign(Date=daily_consumption[daily_consumption['Device Name'] == device]['Date'].dt.strftime('%Y-%m-%d'))
    .to_dict(orient='records')
    for device in daily_consumption['Device Name'].unique()
}

# 存成 JSON 檔案
json_file = "devices_data.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(devices_data, f, ensure_ascii=False, indent=4)

# 產生 HTML 檔案
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Device Power Consumption</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; text-align: center; }}
        .container {{ margin: 20px; padding: 20px; }}
        .chart-container {{ width: 80%; margin: auto; }}
    </style>
</head>
<body>
    <h2>📊 Device Power Consumption Trend</h2>
    <div id="chart" class="chart-container"></div>
    <script>
        let devices = {json.dumps(devices_data, ensure_ascii=False)};
        let traces = [];
        let colors = ['#FF5733', '#33FF57', '#5733FF', '#FFD700', '#FF33A1'];

        let colorIndex = 0;
        for (let device in devices) {{
            let data = devices[device];
            traces.push({{
                x: data.map(d => d["Date"]),
                y: data.map(d => d["Energy Consumption (kWh)"]),
                mode: 'lines+markers',
                name: device,
                line: {{ color: colors[colorIndex % colors.length], width: 2 }}
            }});
            colorIndex++;
        }}

        let layout = {{
            title: 'Daily Device Power Consumption (kWh)',
            xaxis: {{ title: 'Date', tickangle: -45 }},
            yaxis: {{ title: 'Power Consumption (kWh)' }},
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#eef2f7',
            font: {{ family: "Arial", size: 14, color: "#333" }}
        }};

        Plotly.newPlot('chart', traces, layout);
    </script>
</body>
</html>"""

html_file = "power_consumption.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ JSON 檔案已生成: {json_file}")
print(f"✅ HTML 檔案已生成: {html_file}")
