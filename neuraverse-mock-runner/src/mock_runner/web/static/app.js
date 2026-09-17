// Neuraverse Mock Runner — Web UI (Figma design)

const API = '';
let nodes = [];
let selectedNode = null;
let configPairs = [];
let darkMode = false;
let dynamicConfig = null;
let isInitialized = false;

// SVG icon helpers
const ICONS = {
    send: '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    arrow: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    info: '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    warning: '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    error: '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    debug: '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2l1.88 1.88M14.12 3.88L16 2M9 7.13v-1a3.003 3.003 0 1 1 6 0v1"/><path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6"/></svg>',
    x: '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
};

// --- Init ---
async function init() {
    try {
        const resp = await fetch(`${API}/api/nodes`);
        nodes = await resp.json();
        renderNodeList();
        pollState();
    } catch (e) {
        toast('Failed to load nodes: ' + e.message, 'error');
    }
}

// --- Dark Mode ---
function toggleDarkMode() {
    darkMode = !darkMode;
    document.body.classList.toggle('dark', darkMode);
    document.getElementById('icon-moon').style.display = darkMode ? 'none' : '';
    document.getElementById('icon-sun').style.display = darkMode ? '' : 'none';
}

// --- Tabs ---
function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    btn.classList.add('active');
}

// --- Node List ---
function renderNodeList() {
    const list = document.getElementById('node-list');
    list.innerHTML = '';
    nodes.forEach(node => {
        const li = document.createElement('li');
        li.className = selectedNode === node.name ? 'active' : '';
        li.innerHTML = `<div class="node-name">${esc(node.name)}</div><div class="node-desc">${esc(node.description || '')}</div>`;
        li.onclick = () => selectNode(node.name);
        list.appendChild(li);
    });
}

function selectNode(name) {
    selectedNode = name;
    dynamicConfig = null;
    isInitialized = false;
    renderNodeList();
    showConfigSection(name);
    // Show active content, hide empty state
    document.getElementById('empty-state').style.display = 'none';
    document.getElementById('active-content').style.display = '';
    // Enable Execute immediately (it auto-configures before running)
    document.getElementById('btn-execute').disabled = false;
    document.getElementById('btn-stop').disabled = true;
    toast(`Selected node: ${name}`, 'success');
}

// --- Configuration ---
async function showConfigSection(name) {
    const section = document.getElementById('config-section');
    section.style.display = 'block';
    document.getElementById('config-desc').textContent = `Key-value parameters for ${name}`;

    // Reset dynamic config state
    dynamicConfig = null;
    isInitialized = false;
    document.getElementById('legacy-config-buttons').style.display = '';

    const resp = await fetch(`${API}/api/nodes/${name}/schema`);
    const data = await resp.json();
    const schema = data.schema;
    configPairs = [];
    if (schema && schema.configuration) {
        Object.entries(schema.configuration).forEach(([k, v]) => {
            configPairs.push({ key: k, value: typeof v === 'string' ? v : '' });
        });
    }
    renderConfigFields();
}

function renderConfigFields() {
    const container = document.getElementById('config-fields');
    container.innerHTML = '';
    configPairs.forEach((pair, idx) => {
        const div = document.createElement('div');
        div.className = 'config-row';
        div.innerHTML = `
            <input type="text" value="${esc(pair.key)}" onchange="configPairs[${idx}].key=this.value" placeholder="Key" style="flex:1;">
            <input type="text" value="${esc(pair.value)}" onchange="configPairs[${idx}].value=this.value" placeholder="Value" style="flex:1;">
            <button class="btn btn-ghost btn-sm" onclick="configPairs.splice(${idx},1);renderConfigFields()">${ICONS.x}</button>
        `;
        container.appendChild(div);
    });
}

function addConfigField() {
    configPairs.push({ key: '', value: '' });
    renderConfigFields();
}

async function configureNode() {
    if (!selectedNode) return;
    const config = {};
    configPairs.forEach(p => { if (p.key) config[p.key] = p.value; });

    const body = { class_name: selectedNode, config };
    if (isInitialized && dynamicConfig) {
        body.dynamic_config = collectDynamicConfig();
    }

    try {
        const resp = await fetch(`${API}/api/configure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!resp.ok) {
            const err = await resp.json();
            toast(err.detail || 'Configuration failed', 'error');
            return;
        }
        const result = await resp.json();
        toast(`${selectedNode} configured!`, 'success');
        document.getElementById('btn-execute').disabled = false;
        document.getElementById('btn-stop').disabled = false;

        if (result.input_ports && result.input_ports.length > 0) {
            showInjectPanel(result.input_ports);
        } else {
            document.getElementById('inject-ports-container').innerHTML = '<p style="font-size:14px; color:var(--muted-fg);">No input ports available</p>';
        }
        updateState();
        updateStatusLog();
        updateNodeLogs();
    } catch (e) {
        toast('Error: ' + e.message, 'error');
    }
}

// --- Init Node ---
async function initNode() {
    if (!selectedNode) return;
    try {
        const resp = await fetch(`${API}/api/init`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ class_name: selectedNode }),
        });
        if (!resp.ok) {
            const err = await resp.json();
            toast(err.detail || 'Initialization failed', 'error');
            return;
        }
        const result = await resp.json();
        dynamicConfig = result.configuration;
        isInitialized = true;

        if (dynamicConfig && Object.keys(dynamicConfig).length > 0) {
            document.getElementById('config-desc').textContent = `Typed configuration for ${selectedNode}`;
            document.getElementById('legacy-config-buttons').style.display = 'none';
            renderDynamicConfigForm(dynamicConfig);
        } else {
            toast(`${selectedNode} initialized (no configuration)`, 'info');
        }

        toast(`${selectedNode} initialized!`, 'success');
        document.getElementById('btn-execute').disabled = false;
        document.getElementById('btn-stop').disabled = false;
        updateState();
        updateStatusLog();
        updateNodeLogs();
    } catch (e) {
        toast('Error: ' + e.message, 'error');
    }
}

function renderDynamicConfigForm(config) {
    const container = document.getElementById('config-fields');
    container.innerHTML = '';

    for (const [key, entry] of Object.entries(config)) {
        const div = document.createElement('div');
        div.className = 'config-entry';

        const label = entry.displayLabel || key;
        const desc = entry.description || '';
        const unit = entry.unit || '';
        const readOnly = entry.readOnly || false;
        const required = entry.required || false;
        const cv = entry.configValue || {};

        let controlHtml = '';

        if (cv.toggleValue !== undefined && cv.toggleValue !== null && typeof cv.toggleValue === 'object') {
            const isOn = cv.toggleValue.enabled;
            controlHtml = `<div class="switch-row">
                <button class="switch ${isOn ? 'on' : ''}" id="dyn-${esc(key)}"
                    onclick="this.classList.toggle('on')" ${readOnly ? 'disabled' : ''}></button>
            </div>`;
        } else if (cv.rangeValue !== undefined && cv.rangeValue !== null && typeof cv.rangeValue === 'object') {
            const rv = cv.rangeValue;
            controlHtml = `<div class="range-control">
                <input type="range" id="dyn-${esc(key)}"
                    min="${rv.min}" max="${rv.max}" step="${rv.step}" value="${rv.value}"
                    oninput="document.getElementById('dyn-${esc(key)}-display').textContent=this.value"
                    ${readOnly ? 'disabled' : ''}>
                <span id="dyn-${esc(key)}-display" class="range-value">${rv.value}</span>
                ${unit ? `<span class="range-unit">${esc(unit)}</span>` : ''}
            </div>`;
        } else if (cv.singleSelectListValue !== undefined && cv.singleSelectListValue !== null && typeof cv.singleSelectListValue === 'object') {
            const ssl = cv.singleSelectListValue;
            const options = (ssl.allowedItems || []).map(item =>
                `<option value="${esc(item)}" ${item === ssl.selectedItem ? 'selected' : ''}>${esc(item)}</option>`
            ).join('');
            controlHtml = `<select id="dyn-${esc(key)}" ${readOnly ? 'disabled' : ''}>${options}</select>`;
        } else if (cv.multiSelectListValue !== undefined && cv.multiSelectListValue !== null && typeof cv.multiSelectListValue === 'object') {
            const msl = cv.multiSelectListValue;
            const selected = msl.selectedItems || [];
            const checks = (msl.allowedItems || []).map(item =>
                `<label class="checkbox-label">
                    <input type="checkbox" name="dyn-${esc(key)}" value="${esc(item)}"
                        ${selected.includes(item) ? 'checked' : ''} ${readOnly ? 'disabled' : ''}>
                    ${esc(item)}
                </label>`
            ).join('');
            controlHtml = `<div class="multi-select" id="dyn-${esc(key)}">${checks}</div>`;
        } else {
            // String value (default)
            const strVal = cv.stringValue !== undefined ? cv.stringValue : '';
            controlHtml = `<input type="text" id="dyn-${esc(key)}" value="${esc(strVal)}" ${readOnly ? 'disabled' : ''}>`;
        }

        div.innerHTML = `
            <label class="config-label">${esc(label)}${required ? ' <span class="required">*</span>' : ''}</label>
            ${desc ? `<p class="config-desc">${esc(desc)}</p>` : ''}
            ${controlHtml}
        `;
        container.appendChild(div);
    }
}

function collectDynamicConfig() {
    if (!dynamicConfig) return null;
    const result = {};
    for (const [key, entry] of Object.entries(dynamicConfig)) {
        const newEntry = JSON.parse(JSON.stringify(entry));
        const cv = newEntry.configValue || {};

        if (cv.toggleValue !== undefined && cv.toggleValue !== null && typeof cv.toggleValue === 'object') {
            const el = document.getElementById(`dyn-${key}`);
            if (el) cv.toggleValue.enabled = el.classList.contains('on');
        } else if (cv.rangeValue !== undefined && cv.rangeValue !== null && typeof cv.rangeValue === 'object') {
            const el = document.getElementById(`dyn-${key}`);
            if (el) cv.rangeValue.value = parseFloat(el.value);
        } else if (cv.singleSelectListValue !== undefined && cv.singleSelectListValue !== null && typeof cv.singleSelectListValue === 'object') {
            const el = document.getElementById(`dyn-${key}`);
            if (el) cv.singleSelectListValue.selectedItem = el.value;
        } else if (cv.multiSelectListValue !== undefined && cv.multiSelectListValue !== null && typeof cv.multiSelectListValue === 'object') {
            const checkboxes = document.querySelectorAll(`input[name="dyn-${key}"]:checked`);
            cv.multiSelectListValue.selectedItems = Array.from(checkboxes).map(cb => cb.value);
        } else {
            // String value
            const el = document.getElementById(`dyn-${key}`);
            if (el) cv.stringValue = el.value;
        }

        newEntry.configValue = cv;
        result[key] = newEntry;
    }
    return result;
}

// --- Execute ---
async function executeNode() {
    try {
        document.getElementById('btn-execute').disabled = true;

        // Only auto-configure if not already configured (avoids wiping injected data)
        const stateResp = await fetch(`${API}/api/state`);
        const stateData = await stateResp.json();
        if (stateData.state === 'NO_NODE' || stateData.state === 'STOPPED' || stateData.node_name !== selectedNode) {
            const config = {};
            configPairs.forEach(p => { if (p.key) config[p.key] = p.value; });
            const confBody = { class_name: selectedNode, config };
            if (isInitialized && dynamicConfig) {
                confBody.dynamic_config = collectDynamicConfig();
            }
            const confResp = await fetch(`${API}/api/configure`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(confBody),
            });
            if (!confResp.ok) {
                const err = await confResp.json();
                toast(err.detail || 'Configuration failed', 'error');
                return;
            }
            const confResult = await confResp.json();
            if (confResult.input_ports && confResult.input_ports.length > 0) {
                await showInjectPanel(confResult.input_ports);
            }
        }

        // Execute
        const resp = await fetch(`${API}/api/execute`, { method: 'POST' });
        const result = await resp.json();
        if (result.success) {
            toast(`Executed in ${result.execution_time}s`, 'success');
            renderOutputs(result.outputs);
        } else {
            toast('Execution failed: ' + result.error, 'error');
            if (result.outputs) renderOutputs(result.outputs);
        }
        updateState();
        updateStatusLog();
        updateNodeLogs();
    } catch (e) {
        toast('Error: ' + e.message, 'error');
    } finally {
        document.getElementById('btn-execute').disabled = false;
        document.getElementById('btn-stop').disabled = false;
    }
}

// --- Stop ---
async function stopNode() {
    try {
        await fetch(`${API}/api/stop`, { method: 'POST' });
        toast('Node stopped', 'info');
        document.getElementById('btn-execute').disabled = true;
        document.getElementById('btn-stop').disabled = true;
        updateState();
        updateStatusLog();
    } catch (e) {
        toast('Error: ' + e.message, 'error');
    }
}

// --- Reload ---
async function reloadNodes() {
    try {
        const resp = await fetch(`${API}/api/reload`, { method: 'POST' });
        const result = await resp.json();
        if (result.success) {
            const nodesResp = await fetch(`${API}/api/nodes`);
            nodes = await nodesResp.json();
            renderNodeList();
            if (result.reconfigured) {
                toast(`Code reloaded. ${result.reconfigured} re-configured.`, 'success');
                document.getElementById('btn-execute').disabled = false;
                document.getElementById('btn-stop').disabled = false;
            } else {
                toast(`Code reloaded. ${result.nodes.length} node(s) found.`, 'success');
            }
            updateState();
            updateNodeLogs();
        }
    } catch (e) {
        toast('Error: ' + e.message, 'error');
    }
}

// --- Inject ---
async function showInjectPanel(ports) {
    const container = document.getElementById('inject-ports-container');
    if (!ports || ports.length === 0) {
        container.innerHTML = '<p style="font-size:14px; color:var(--muted-fg);">No input ports available</p>';
        return;
    }
    container.innerHTML = '';

    for (const port of ports) {
        const portName = port.name;
        const rosType = port.ros_type || '';
        let schema = null;
        if (rosType) {
            try {
                const resp = await fetch(`${API}/api/ros-types/${encodeURIComponent(rosType)}`);
                schema = await resp.json();
            } catch (e) { }
        }

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${esc(portName)}</div>
                <div class="card-desc">Type: ${esc(rosType)}</div>
            </div>
            <div class="card-body">
                <div class="inject-fields" id="inject-fields-${esc(portName)}"></div>
                <div class="card-row-end">
                    <button class="btn btn-outline btn-sm" onclick="injectPort('${esc(portName)}', '${esc(rosType)}')">
                        ${ICONS.send} Inject
                    </button>
                </div>
            </div>
        `;
        container.appendChild(card);
        renderInjectFields(card.querySelector('.inject-fields'), portName, schema);
    }
}

function renderInjectFields(container, portName, schema) {
    if (!schema || !schema.fields) {
        container.innerHTML = `<div class="port-field"><label class="small">Data (JSON)</label><textarea id="inject-val-${esc(portName)}-json" style="width:100%; min-height:60px; font-family:var(--font-mono); font-size:12px; background:var(--input-bg); border:1px solid var(--border); border-radius:6px; color:var(--fg); padding:8px;" placeholder='{"key": "value"}'></textarea></div>`;
        return;
    }
    schema.fields.forEach(field => {
        const fieldId = `inject-val-${portName}-${field.name}`;
        const div = document.createElement('div');
        div.className = 'port-field';

        if (field.type === 'bool') {
            div.innerHTML = `<div class="switch-row"><label>${esc(field.label)}</label><button class="switch" id="${esc(fieldId)}" onclick="this.classList.toggle('on')"></button></div>`;
        } else if (field.type === 'float' || field.type === 'int') {
            div.innerHTML = `<label class="small">${esc(field.label)}</label><input type="number" id="${esc(fieldId)}" step="${field.type === 'float' ? '0.01' : '1'}" value="0">`;
        } else if (field.type === 'float_array' || field.type === 'int_array') {
            div.innerHTML = `<label class="small">${esc(field.label)}</label><input type="text" id="${esc(fieldId)}" placeholder="1.0, 2.0, 3.0">`;
        } else if (field.type === 'json') {
            div.innerHTML = `<label class="small">${esc(field.label)}</label><textarea id="${esc(fieldId)}" style="width:100%; min-height:60px; font-family:var(--font-mono); font-size:12px; background:var(--input-bg); border:1px solid var(--border); border-radius:6px; color:var(--fg); padding:8px;" placeholder='{"key": "value"}'></textarea>`;
        } else if (field.type === 'base64') {
            div.innerHTML = `<label class="small">${esc(field.label)}</label><input type="file" id="${esc(fieldId)}-file" onchange="fileToBase64('${esc(fieldId)}', this)"><input type="hidden" id="${esc(fieldId)}">`;
        } else {
            div.innerHTML = `<label class="small">${esc(field.label)}</label><input type="text" id="${esc(fieldId)}" placeholder="Enter value...">`;
        }
        container.appendChild(div);
    });
}

function fileToBase64(targetId, fileInput) {
    const file = fileInput.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
        document.getElementById(targetId).value = reader.result.split(',')[1];
        toast(`File loaded: ${file.name}`, 'success');
    };
    reader.readAsDataURL(file);
}

async function injectPort(portName, rosType) {
    const fields = {};
    document.querySelectorAll(`[id^="inject-val-${portName}-"]`).forEach(el => {
        if (el.type === 'file') return;
        const key = el.id.replace(`inject-val-${portName}-`, '');
        if (el.type === 'hidden') { fields[key] = el.value; return; }
        if (el.classList.contains('switch')) { fields[key] = el.classList.contains('on'); return; }
        if (el.type === 'number') { fields[key] = el.value; return; }
        if (el.tagName === 'TEXTAREA') { try { fields[key] = JSON.parse(el.value); } catch { fields[key] = el.value; } return; }
        fields[key] = el.value;
    });

    try {
        const resp = await fetch(`${API}/api/inject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ port_name: portName, ros_type: rosType, fields }),
        });
        if (resp.ok) toast(`Data injected to ${portName}`, 'success');
        else { const err = await resp.json(); toast(err.detail || 'Injection failed', 'error'); }
    } catch (e) { toast('Error: ' + e.message, 'error'); }
}

// --- Outputs ---
function renderOutputs(outputs) {
    const container = document.getElementById('outputs-container');
    if (!outputs || Object.keys(outputs).length === 0) {
        container.innerHTML = '<p style="font-size:14px; color:var(--muted-fg);">No outputs published yet</p>';
        return;
    }
    container.innerHTML = '';
    for (const [port, messages] of Object.entries(outputs)) {
        messages.forEach(msg => {
            const card = document.createElement('div');
            card.className = 'card output-card';
            const now = new Date().toLocaleTimeString();
            card.innerHTML = `
                <div class="card-header"><div><div class="card-title">${esc(port)}</div></div><span class="output-time">${now}</span></div>
                <div class="card-body"><div class="output-data">${esc(typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2))}</div></div>
            `;
            container.appendChild(card);
        });
    }
}

function clearOutputs() {
    document.getElementById('outputs-container').innerHTML = '<p style="font-size:14px; color:var(--muted-fg);">No outputs published yet</p>';
    toast('Outputs cleared', 'success');
}

// --- State ---
async function updateState() {
    try {
        const resp = await fetch(`${API}/api/state`);
        const data = await resp.json();
        const badge = document.getElementById('state-badge');
        badge.textContent = data.state;
        badge.className = 'state-badge state-' + data.state;
        const nodeName = document.getElementById('current-node');
        const divider = document.getElementById('header-divider');
        if (data.node_name) {
            nodeName.textContent = data.node_name;
            divider.style.display = '';
        } else {
            nodeName.textContent = '';
            divider.style.display = 'none';
        }
    } catch (e) { }
}

function pollState() { setInterval(updateState, 2000); }

// --- Status Log ---
async function updateStatusLog() {
    try {
        const resp = await fetch(`${API}/api/status-log`);
        const log = await resp.json();
        const container = document.getElementById('status-log');
        if (!log || log.length === 0) {
            container.innerHTML = '<p style="font-size:14px; color:var(--muted-fg);">No state transitions yet</p>';
            return;
        }
        container.innerHTML = '';
        log.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'status-entry';
            const time = (entry.resultMessage || '').match(/from (\w+)/)?.[1] || '';
            const toState = entry.state_name || '?';
            div.innerHTML = `
                <span class="status-time">${esc(new Date().toLocaleTimeString())}</span>
                ${time ? `<span class="status-from">${esc(time)}</span><span class="status-arrow">${ICONS.arrow}</span>` : ''}
                <span class="status-to">${esc(toState)}</span>
            `;
            container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
    } catch (e) { }
}

// --- Node Logs ---
async function updateNodeLogs() {
    try {
        const resp = await fetch(`${API}/api/logs`);
        const logs = await resp.json();
        const container = document.getElementById('node-logs');
        if (!logs || logs.length === 0) {
            container.innerHTML = '<p style="font-size:14px; color:var(--muted-fg);">No logs yet</p>';
            return;
        }
        container.innerHTML = '';
        logs.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'log-entry';
            const level = entry.level.toLowerCase();
            const icon = ICONS[level] || ICONS.info;
            const time = entry.timestamp ? entry.timestamp.split('T')[1] : '';
            div.innerHTML = `
                <span class="log-badge log-badge-${level}">${icon} ${esc(entry.level)}</span>
                <span class="log-time">${esc(time)}</span>
                <span class="log-message">${esc(entry.message)}</span>
            `;
            container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
    } catch (e) { }
}

// --- Utilities ---
function esc(str) {
    if (str === undefined || str === null) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function toast(msg, type) {
    const div = document.createElement('div');
    div.className = 'toast toast-' + type;
    div.textContent = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

// --- Sidebar Resize ---
(function() {
    const handle = document.getElementById('sidebar-resize-handle');
    const sidebar = document.querySelector('.sidebar');
    let dragging = false;

    handle.addEventListener('mousedown', (e) => {
        e.preventDefault();
        dragging = true;
        handle.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (!dragging) return;
        const newWidth = Math.min(Math.max(e.clientX, 220), window.innerWidth * 0.6);
        sidebar.style.width = newWidth + 'px';
    });

    document.addEventListener('mouseup', () => {
        if (!dragging) return;
        dragging = false;
        handle.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    });
})();

// --- Start ---
init();
