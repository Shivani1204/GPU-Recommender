from flask import Flask, render_template_string, request, jsonify
import json

app = Flask(__name__)

# GPU recommendation logic based on your PlantUML flowchart
def get_gpu_recommendation(model_size, throughput_needs, budget):
    recommendations = {
        "≤3B": {
            "gpu": "T4",
            "specs": "~130 INT8 TOPS",
            "cost": "$0.3-0.6M tokens",
            "framework": "Ollama + INT8",
            "description": "Basic entry-level solution for small models",
            "color": "linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%)"
        },
        "3-7B": {
            "gpu": "T4 Pro",
            "specs": "~180 INT8 TOPS",
            "cost": "$0.6-1.2M tokens",
            "framework": "Ollama + INT8/FP16",
            "description": "Enhanced T4 for medium-small models",
            "color": "linear-gradient(135deg, #FF8C42 0%, #FFB347 100%)"
        },
        "7-13B": {
            "gpu": "RTX 4090",
            "specs": "~330 INT8 TOPS",
            "cost": "$1.5-3k hardware",
            "framework": "vLLM + INT8",
            "description": "Consumer-grade high performance",
            "color": "linear-gradient(135deg, #FFB347 0%, #FF6B35 100%)"
        },
        "13-30B": {
            "gpu": "A10",
            "specs": "~640 INT8 TOPS",
            "cost": "$3-8k cloud/month",
            "framework": "vLLM/TensorRT + INT8/FP8",
            "description": "Professional mid-tier solution",
            "color": "linear-gradient(135deg, #FF6B35 0%, #D2691E 100%)"
        },
        "30-70B": {
            "gpu": "A100",
            "specs": "~1248 INT8 TOPS",
            "cost": "$8-20k cloud/month",
            "framework": "INT4/FP8 & TensorRT-LLM",
            "description": "Enterprise-grade performance",
            "color": "linear-gradient(135deg, #D2691E 0%, #8B4513 100%)"
        },
        "70B+": {
            "gpu": "H100",
            "specs": "~2500 INT8 TOPS",
            "cost": "$20k+ cloud/month",
            "framework": "Advanced multi-GPU optimization",
            "description": "Top-tier enterprise solution",
            "color": "linear-gradient(135deg, #8B4513 0%, #1A1A1A 100%)"
        }
    }
    
    # More detailed logic based on all three parameters
    if model_size == "≤3B":
        return recommendations["≤3B"]
    elif model_size == "3-7B":
        return recommendations["3-7B"]
    elif model_size == "7-13B":
        return recommendations["7-13B"]
    elif model_size == "13-30B":
        return recommendations["13-30B"]
    elif model_size == "30-70B":
        if throughput_needs in ["high", "very_high"] or budget == "high":
            return recommendations["30-70B"]
        else:
            return recommendations["13-30B"]
    elif model_size == "70B+":
        return recommendations["70B+"]
    
    return recommendations["≤3B"]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPU Selection Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #FF6B35 0%, #1A1A1A 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: #1F1F1F;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            animation: slideIn 0.5s ease-out;
            border: 2px solid #FF6B35;
        }
        
        @keyframes slideIn {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        h1 {
            color: #FF6B35;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #FF6B35;
            font-weight: 500;
            font-size: 1.1em;
        }
        
        select, input {
            width: 100%;
            padding: 15px;
            border: 2px solid #FF6B35;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #2A2A2A;
            color: #FFFFFF;
        }
        
        select:focus, input:focus {
            outline: none;
            border-color: #FF8C42;
            background: #333333;
            box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.3);
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
            color: #1A1A1A;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .result {
            margin-top: 30px;
            padding: 25px;
            border-radius: 15px;
            display: none;
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .result h3 {
            font-size: 1.8em;
            margin-bottom: 15px;
            color: white;
        }
        
        .result-content {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .result-item {
            margin-bottom: 10px;
            color: white;
            font-size: 1.1em;
        }
        
        .result-item strong {
            color: #fff;
        }
        
        .loading {
            text-align: center;
            color: #FF6B35;
            font-size: 1.2em;
            margin-top: 20px;
        }
        
        .gpu-icon {
            font-size: 2em;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .flowchart-info {
            background: rgba(255, 107, 53, 0.1);
            border-left: 4px solid #FF6B35;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        
        .flowchart-info h4 {
            color: #FF6B35;
            margin-bottom: 10px;
        }
        
        .flowchart-info p {
            color: #CCCCCC;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>GPU Recommender</h1>
        
        <div class="flowchart-info">
            <h4>GPU Recommender System</h4>
            <p>This tool helps you select the optimal GPU for your machine learning workloads based on model size, throughput requirements, and budget constraints.</p>
        </div>
        
        <form id="gpuForm">
            <div class="form-group">
                <label for="model_size">Model Size:</label>
                <select id="model_size" name="model_size" required>
                    <option value="">Select model size...</option>
                    <option value="≤3B">≤3B Parameters (Small)</option>
                    <option value="3-7B">3-7B Parameters (Medium-Small)</option>
                    <option value="7-13B">7-13B Parameters (Medium)</option>
                    <option value="13-30B">13-30B Parameters (Large)</option>
                    <option value="30-70B">30-70B Parameters (Very Large)</option>
                    <option value="70B+">70B+ Parameters (Massive)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="throughput_needs">Throughput Requirements:</label>
                <select id="throughput_needs" name="throughput_needs" required>
                    <option value="">Select throughput needs...</option>
                    <option value="very_low">Very Low (Research/Testing)</option>
                    <option value="low">Low (Development)</option>
                    <option value="medium">Medium (Small Production)</option>
                    <option value="high">High (Production Scale)</option>
                    <option value="very_high">Very High (Enterprise Scale)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="budget">Budget Range:</label>
                <select id="budget" name="budget" required>
                    <option value="">Select budget range...</option>
                    <option value="very_low">Very Low ($200-$800)</option>
                    <option value="low">Low ($800-$2,000)</option>
                    <option value="medium">Medium ($2,000-$8,000)</option>
                    <option value="high">High ($8,000-$20,000)</option>
                    <option value="very_high">Very High ($20,000+)</option>
                </select>
            </div>
            
            <button type="submit" class="btn">Get GPU Recommendation</button>
        </form>
        
        <div id="loading" class="loading" style="display: none;">
            Analyzing your requirements...
        </div>
        
        <div id="result" class="result">
            <div class="gpu-icon"></div>
            <h3>Recommended GPU Solution</h3>
            <div class="result-content">
                <div class="result-item"><strong>GPU:</strong> <span id="gpu-name"></span></div>
                <div class="result-item"><strong>Specifications:</strong> <span id="gpu-specs"></span></div>
                <div class="result-item"><strong>Cost:</strong> <span id="gpu-cost"></span></div>
                <div class="result-item"><strong>Framework:</strong> <span id="gpu-framework"></span></div>
                <div class="result-item"><strong>Description:</strong> <span id="gpu-description"></span></div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('gpuForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                model_size: formData.get('model_size'),
                throughput_needs: formData.get('throughput_needs'),
                budget: formData.get('budget')
            };
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            // Simulate API call delay
            setTimeout(() => {
                fetch('/api/recommend', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    document.getElementById('loading').style.display = 'none';
                    
                    // Update result display
                    document.getElementById('gpu-name').textContent = result.gpu;
                    document.getElementById('gpu-specs').textContent = result.specs;
                    document.getElementById('gpu-cost').textContent = result.cost;
                    document.getElementById('gpu-framework').textContent = result.framework;
                    document.getElementById('gpu-description').textContent = result.description;
                    
                    // Set result background color
                    const resultDiv = document.getElementById('result');
                    resultDiv.style.background = result.color;
                    resultDiv.style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error getting recommendation. Please try again.');
                });
            }, 1000);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    model_size = data.get('model_size')
    throughput_needs = data.get('throughput_needs')
    budget = data.get('budget')
    
    recommendation = get_gpu_recommendation(model_size, throughput_needs, budget)
    return jsonify(recommendation)

# WSGI handler for Vercel
from flask import Response
def handler(environ, start_response):
    return app.wsgi_app(environ, start_response)


if __name__ == '__main__':
    app.run(debug=True)
