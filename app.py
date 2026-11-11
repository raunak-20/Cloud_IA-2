import os
import socket
import time
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

START_TIME = time.time()
REQUEST_COUNT = 0
APP_VERSION = os.environ.get("APP_VERSION", "1.0")


@app.before_request
def count_requests():
    global REQUEST_COUNT
    REQUEST_COUNT += 1


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask on Kubernetes</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background-color: #0d131f;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 40px 20px;
        }
        .container {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        header h1 {
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
        }
        .version-badge {
            background: rgba(59, 130, 246, 0.1);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 9999px;
            padding: 4px 14px;
            font-size: 13px;
            font-family: monospace;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 640px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }
        .card {
            background-color: #162032;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }
        .card-header-label {
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .card h2 {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
        }
        .card-desc {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 16px;
            line-height: 1.4;
        }
        .pod-hostname {
            color: #fcd34d;
            font-size: 20px;
            font-weight: 700;
            font-family: monospace;
            word-break: break-all;
            margin-bottom: 16px;
        }
        .metrics-row {
            display: flex;
            gap: 32px;
            margin-bottom: 20px;
        }
        .metric-item .label {
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 4px;
        }
        .metric-item .val {
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
        }
        .btn {
            background-color: #243247;
            color: #f1f5f9;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px 18px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn:hover {
            background-color: #334155;
        }
        .btn-primary {
            background-color: #2563eb;
            border-color: #3b82f6;
            color: #ffffff;
        }
        .btn-primary:hover {
            background-color: #1d4ed8;
        }
        .btn-success {
            background-color: #10b981;
            border-color: #34d399;
            color: #ffffff;
        }
        .btn-success:hover {
            background-color: #059669;
        }
        .health-status {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 17px;
            font-weight: 600;
            color: #22c55e;
            margin-bottom: 18px;
        }
        .dot {
            width: 10px;
            height: 10px;
            background-color: #22c55e;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #22c55e;
        }
        .health-note {
            font-size: 13px;
            color: #64748b;
            margin-top: 14px;
            line-height: 1.4;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .summary-stats {
            display: flex;
            gap: 24px;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #1e293b;
        }
        .summary-stats .stat-box .stat-label {
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 2px;
        }
        .summary-stats .stat-box .stat-number {
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
        }
        .pod-bar-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .pod-bar-row {
            display: flex;
            align-items: center;
            gap: 14px;
            font-family: monospace;
            font-size: 13px;
        }
        .pod-bar-name {
            width: 240px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            color: #cbd5e1;
        }
        .pod-bar-track {
            flex: 1;
            height: 12px;
            background-color: #0d131f;
            border-radius: 6px;
            overflow: hidden;
        }
        .pod-bar-fill {
            height: 100%;
            background-color: #f59e0b;
            border-radius: 6px;
            transition: width 0.3s ease;
        }
        .pod-bar-count {
            width: 35px;
            text-align: right;
            font-weight: 700;
            color: #f1f5f9;
        }
        .live-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 38px;
            align-items: center;
        }
        .pod-badge {
            background-color: #fde047;
            color: #0f172a;
            font-weight: 700;
            font-size: 12px;
            font-family: monospace;
            padding: 4px 10px;
            border-radius: 9999px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        footer {
            font-size: 13px;
            color: #64748b;
            text-align: center;
            line-height: 1.6;
            margin-top: 10px;
        }
        footer a {
            color: #94a3b8;
            text-decoration: none;
        }
        footer code {
            font-family: monospace;
            color: #94a3b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Flask on Kubernetes</h1>
            <div class="version-badge">version {{ version }}</div>
        </header>

        <div class="grid-2">
            <!-- Served by pod card -->
            <div class="card">
                <div class="card-header-label">Served by pod</div>
                <div class="pod-hostname" id="pod-hostname">{{ pod_hostname }}</div>
                <div class="metrics-row">
                    <div class="metric-item">
                        <div class="label">Requests on this pod</div>
                        <div class="val" id="pod-requests">{{ requests_count }}</div>
                    </div>
                    <div class="metric-item">
                        <div class="label">Pod uptime</div>
                        <div class="val" id="pod-uptime">{{ uptime }}</div>
                    </div>
                </div>
                <button class="btn" onclick="refreshPodInfo()">Refresh</button>
            </div>

            <!-- Health check card -->
            <div class="card">
                <div class="card-header-label">Health Check (/health)</div>
                <div class="health-status" id="health-status">
                    <span class="dot"></span>
                    <span>healthy (200 OK)</span>
                </div>
                <button class="btn" onclick="checkHealth()">Check health</button>
                <div class="health-note">
                    Kubernetes calls this endpoint for its readiness and liveness probes.
                </div>
            </div>
        </div>

        <!-- Load balancing card -->
        <div class="card">
            <h2>Load balancing</h2>
            <div class="card-desc">Sends requests to this app and counts which pod answered each one.</div>
            <div class="btn-group">
                <button class="btn btn-primary" id="btn-send-requests" onclick="sendBatchRequests(30)">Send 30 requests</button>
                <button class="btn" onclick="resetLoadBalancing()">Reset</button>
            </div>
            <div class="summary-stats">
                <div class="stat-box">
                    <div class="stat-label">Sent</div>
                    <div class="stat-number" id="stats-sent">0</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Succeeded</div>
                    <div class="stat-number" id="stats-succ">0</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Failed</div>
                    <div class="stat-number" id="stats-fail">0</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Pods seen</div>
                    <div class="stat-number" id="stats-pods">0</div>
                </div>
            </div>
            <div class="pod-bar-list" id="pod-bars">
                <!-- Pod bars rendered dynamically -->
            </div>
        </div>

        <!-- Live monitor card -->
        <div class="card">
            <h2>Live monitor</h2>
            <div class="card-desc">Polls every second. Delete a pod with <code>kubectl delete pod</code> and watch the traffic move on to the other pods.</div>
            <div style="margin-bottom: 16px;">
                <button class="btn" id="live-toggle-btn" onclick="toggleLiveMonitor()">Start live monitor</button>
            </div>
            <div class="live-badges" id="live-badges">
                <!-- Short pod names added dynamically -->
            </div>
        </div>

        <footer>
            Endpoints: <code>/</code> this page · <code>/api/info</code> JSON · <code>/health</code> probe. 
            Through kubectl port-forward every request goes to one pod; through the NodePort ( :30007 ) requests spread across all pods.
        </footer>
    </div>

    <script>
        let lbData = {
            sent: 0,
            succeeded: 0,
            failed: 0,
            pods: {}
        };

        function formatUptime(seconds) {
            if (seconds < 60) return seconds + 's';
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            return m + 'm ' + s + 's';
        }

        async function refreshPodInfo() {
            try {
                const res = await fetch('/api/info');
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('pod-hostname').innerText = data.pod_hostname;
                    document.getElementById('pod-requests').innerText = data.requests_on_pod;
                    document.getElementById('pod-uptime').innerText = formatUptime(data.uptime_seconds);
                }
            } catch (err) {
                console.error(err);
            }
        }

        async function checkHealth() {
            const statusEl = document.getElementById('health-status');
            statusEl.innerHTML = '<span class="dot" style="background:#eab308; box-shadow:0 0 10px #eab308;"></span><span>checking...</span>';
            try {
                const res = await fetch('/health');
                if (res.ok) {
                    const data = await res.json();
                    statusEl.innerHTML = '<span class="dot"></span><span>healthy (200 OK)</span>';
                } else {
                    statusEl.innerHTML = '<span class="dot" style="background:#ef4444; box-shadow:0 0 10px #ef4444;"></span><span>unhealthy (' + res.status + ')</span>';
                }
            } catch (err) {
                statusEl.innerHTML = '<span class="dot" style="background:#ef4444; box-shadow:0 0 10px #ef4444;"></span><span>offline</span>';
            }
        }

        function updateLbUI() {
            document.getElementById('stats-sent').innerText = lbData.sent;
            document.getElementById('stats-succ').innerText = lbData.succeeded;
            document.getElementById('stats-fail').innerText = lbData.failed;
            const podKeys = Object.keys(lbData.pods);
            document.getElementById('stats-pods').innerText = podKeys.length;

            const barsContainer = document.getElementById('pod-bars');
            barsContainer.innerHTML = '';
            
            let maxCount = 1;
            for (const p in lbData.pods) {
                if (lbData.pods[p] > maxCount) maxCount = lbData.pods[p];
            }

            for (const pod of podKeys) {
                const count = lbData.pods[pod];
                const pct = Math.round((count / maxCount) * 100);
                const row = document.createElement('div');
                row.className = 'pod-bar-row';
                row.innerHTML = `
                    <div class="pod-bar-name" title="${pod}">${pod}</div>
                    <div class="pod-bar-track">
                        <div class="pod-bar-fill" style="width: ${pct}%"></div>
                    </div>
                    <div class="pod-bar-count">${count}</div>
                `;
                barsContainer.appendChild(row);
            }
        }

        async function sendBatchRequests(n) {
            const btn = document.getElementById('btn-send-requests');
            btn.disabled = true;
            btn.innerText = 'Sending...';

            for (let i = 0; i < n; i++) {
                lbData.sent++;
                try {
                    const res = await fetch('/api/info');
                    if (res.ok) {
                        const data = await res.json();
                        lbData.succeeded++;
                        const host = data.pod_hostname || 'unknown';
                        lbData.pods[host] = (lbData.pods[host] || 0) + 1;
                    } else {
                        lbData.failed++;
                    }
                } catch (e) {
                    lbData.failed++;
                }
                updateLbUI();
                await new Promise(r => setTimeout(r, 40));
            }

            btn.disabled = false;
            btn.innerText = `Send ${n} requests`;
            refreshPodInfo();
        }

        function resetLoadBalancing() {
            lbData = { sent: 0, succeeded: 0, failed: 0, pods: {} };
            updateLbUI();
        }

        let liveInterval = null;
        function getShortPodName(full) {
            if (!full) return 'unknown';
            const parts = full.split('-');
            return parts[parts.length - 1];
        }

        function toggleLiveMonitor() {
            const btn = document.getElementById('live-toggle-btn');
            const badgesContainer = document.getElementById('live-badges');

            if (liveInterval) {
                clearInterval(liveInterval);
                liveInterval = null;
                btn.innerText = 'Start live monitor';
                btn.className = 'btn';
            } else {
                btn.innerText = 'Stop live monitor';
                btn.className = 'btn btn-success';

                const poll = async () => {
                    try {
                        const res = await fetch('/api/info');
                        if (res.ok) {
                            const data = await res.json();
                            const short = getShortPodName(data.pod_hostname);
                            const badge = document.createElement('span');
                            badge.className = 'pod-badge';
                            badge.innerText = short;
                            badge.title = data.pod_hostname;
                            badgesContainer.appendChild(badge);

                            while (badgesContainer.children.length > 25) {
                                badgesContainer.removeChild(badgesContainer.firstChild);
                            }
                        }
                    } catch (e) {
                        console.error(e);
                    }
                };

                poll();
                liveInterval = setInterval(poll, 1000);
            }
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    user_agent = request.headers.get("User-Agent", "").lower()
    accept = request.headers.get("Accept", "").lower()
    format_arg = request.args.get("format", "").lower()

    # If requested by curl, explicit json format parameter, or JSON-only accept header:
    if format_arg == "json" or "curl" in user_agent or ("application/json" in accept and "text/html" not in accept):
        return jsonify({
            "message": "Hello from a containerized Flask app!",
            "pod_hostname": socket.gethostname(),
            "version": APP_VERSION
        })

    # Otherwise render the visual dashboard for browser access
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = f"{uptime_sec}s" if uptime_sec < 60 else f"{uptime_sec // 60}m {uptime_sec % 60}s"
    return render_template_string(
        DASHBOARD_HTML,
        version=APP_VERSION,
        pod_hostname=socket.gethostname(),
        requests_count=REQUEST_COUNT,
        uptime=uptime_str
    )


@app.route("/api/info")
def api_info():
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = f"{uptime_sec}s" if uptime_sec < 60 else f"{uptime_sec // 60}m {uptime_sec % 60}s"
    return jsonify({
        "pod_hostname": socket.gethostname(),
        "version": APP_VERSION,
        "uptime_seconds": uptime_sec,
        "uptime_human": uptime_str,
        "requests_on_pod": REQUEST_COUNT,
        "status": "healthy"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "pod_hostname": socket.gethostname(),
        "timestamp": time.time()
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

