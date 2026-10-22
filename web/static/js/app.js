const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

function toast(msg) {
    const t = $('#toast');
    if (!t) return;

    t.textContent = msg;
    t.classList.add('show');

    setTimeout(() => {
        t.classList.remove('show');
    }, 2800);
}

async function api(url, opt = {}) {
    const r = await fetch(url, opt);

    let d;

    try {
        d = await r.json();
    } catch (e) {
        throw new Error('API không trả JSON: HTTP ' + r.status);
    }

    if (!r.ok) {
        throw new Error(d.detail || 'API error');
    }

    return d;
}


/* =========================
   NAVIGATION
========================= */

function activeNav() {
    let p = location.pathname;

    let page =
        p === '/'
            ? 'dashboard'
            : p.slice(1).split('/')[0];

    $$('.nav-link').forEach(a => {
        a.classList.toggle(
            'active',
            a.dataset.page === page
        );
    });
}


/* =========================
   AGENT / GNS3 STATUS
========================= */

async function checkAgent() {
    try {
        await api('/health');

        const d = await fetch('/api/gns3');
        const g = await d.json();

        $('#agentStatus')?.replaceChildren(
            document.createTextNode(
                'Ubuntu Agent: Online'
            )
        );

        $('#sysAgent')?.classList.add('ok');

        if ($('#sysAgent')) {
            $('#sysAgent').textContent = 'ONLINE';
        }

        if ($('#sysGns3')) {
            if (g.success) {
                $('#sysGns3').textContent = 'ONLINE';
                $('#sysGns3').className = 'ok';
            } else {
                $('#sysGns3').textContent = 'OFFLINE';
                $('#sysGns3').className = 'failed';
            }
        }

    } catch (e) {

        if ($('#agentStatus')) {
            $('#agentStatus').textContent =
                'Agent: kiểm tra API';
        }
    }
}


/* =========================
   DEVICES
========================= */

async function getDevices() {
    return api('/api/devices');
}


/* =========================
   BACKUPS
========================= */

async function getBackups() {
    return api('/api/backup');
}


function deviceRow(d) {

    return `
        <div class="device-row">

            <div class="device-main">

                <div class="device-icon">
                    ◉
                </div>

                <div>
                    <b>${d.name}</b>

                    <small>
                        ${d.host}:${d.port || 22}
                    </small>
                </div>

            </div>

            <div>
                <span class="status-ok">
                    ● CONFIGURED
                </span>
            </div>

        </div>
    `;
}


/* =========================
   DASHBOARD
========================= */

async function loadDashboard() {

    try {

        const [ds, bs] = await Promise.all([
            getDevices(),
            getBackups()
        ]);

        $('#statDevices').textContent =
            ds.length;

        $('#statBackups').textContent =
            bs.length;

        $('#statChanged').textContent =
            bs.filter(
                x => x.changed === 'YES'
            ).length;

        $('#deviceList').innerHTML =
            ds.map(deviceRow).join('') ||
            '<div class="loading">Chưa có thiết bị</div>';

        $('#recentBackups').innerHTML =
            tableBackups(bs.slice(0, 6));

        $('#statAgent').textContent =
            'ONLINE';

    } catch (e) {

        toast(e.message);
    }
}


function tableBackups(rows) {

    if (!rows.length) {
        return `
            <div class="loading">
                Chưa có backup.
            </div>
        `;
    }

    return `
        <table>

            <thead>
                <tr>
                    <th>Device</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Changed</th>
                </tr>
            </thead>

            <tbody>

                ${rows.map(x => `

                    <tr>

                        <td>
                            ${x.device}
                        </td>

                        <td>
                            ${x.created_at}
                        </td>

                        <td class="${x.status === 'SUCCESS'
                            ? 'success'
                            : 'failed'}">

                            ${x.status}

                        </td>

                        <td class="${x.changed === 'YES'
                            ? 'changed'
                            : ''}">

                            ${x.changed}

                        </td>

                    </tr>

                `).join('')}

            </tbody>

        </table>
    `;
}


/* =========================
   DEVICE PAGE
========================= */

async function loadDevicesPage() {

    const ds = await getDevices();

    $('#devicesTable').innerHTML = `

        <table>

            <thead>

                <tr>
                    <th>Device</th>
                    <th>IP</th>
                    <th>Type</th>
                    <th>SSH</th>
                    <th>Action</th>
                </tr>

            </thead>

            <tbody>

                ${ds.map(d => `

                    <tr>

                        <td>
                            <b>${d.name}</b>
                        </td>

                        <td>
                            ${d.host}
                        </td>

                        <td>
                            ${d.device_type}
                        </td>

                        <td>
                            ${d.legacy_ssh
                                ? 'Legacy / Ubuntu'
                                : 'Netmiko'}
                        </td>

                        <td>

                            <button
                                class="btn"
                                onclick="quickBackup('${d.name}')">

                                Backup

                            </button>

                            <button
                                class="btn"
                                onclick="showMetrics('${d.name}')">

                                Metrics

                            </button>

                        </td>

                    </tr>

                `).join('')}

            </tbody>

        </table>
    `;

    const s = $('#cmdDevice');

    if (s) {

        s.innerHTML = ds.map(d => `
            <option>${d.name}</option>
        `).join('');

    }
}


/* =========================
   BACKUP
========================= */

async function backupAll() {

    try {

        toast('Đang backup...');

        const d = await api(
            '/api/backup',
            {
                method: 'POST'
            }
        );

        toast('Backup hoàn tất');

        if (location.pathname === '/') {
            loadDashboard();
        }

        else if (
            location.pathname === '/backups'
        ) {
            loadBackupsPage();
        }

        return d;

    } catch (e) {

        toast(e.message);
    }
}


async function quickBackup(n) {

    try {

        toast(
            'Đang backup ' + n + '...'
        );

        await api(
            '/api/backup?device=' +
            encodeURIComponent(n),
            {
                method: 'POST'
            }
        );

        toast(
            'Backup ' + n + ' thành công'
        );

        if (
            location.pathname === '/backups'
        ) {
            loadBackupsPage();
        }

        if (location.pathname === '/') {
            loadDashboard();
        }

    } catch (e) {

        toast(e.message);
    }
}


async function loadBackupsPage() {

    const b = await getBackups();

    $('#backupsTable').innerHTML =
        tableBackups(b);
}


/* =========================
   DIFF
========================= */

async function loadDiffPage() {

    const n = $('#diffDevice').value;

    try {

        const d = await api(
            '/api/diff/' +
            encodeURIComponent(n)
        );

        $('#diffMeta').innerHTML = `

            <div class="device-row">

                <span>
                    ${d.message || 'Latest diff'}
                </span>

                <b class="${d.changed
                    ? 'changed'
                    : 'success'}">

                    ${d.changed
                        ? 'CHANGED'
                        : 'NO CHANGE'}

                </b>

            </div>

        `;

        $('#diffOutput').textContent =
            d.diff || 'Không có khác biệt.';

    } catch (e) {

        toast(e.message);
    }
}


async function showDiff(n) {

    location.href =
        '/diff?device=' +
        encodeURIComponent(n);
}


/* =========================
   MONITORING
========================= */




       async function loadMetricsPage() {
    const n = $('#metricDevice').value;

    try {
        const d = await api(
            '/api/metrics/' + encodeURIComponent(n)
        );

        /*
         * API hiện tại:
         *
         * {
         *   device: "R1",
         *   cpu_percent: 0,
         *   memory_used_bytes: 98890848,
         *   raw: {
         *      cpu: "...",
         *      memory: "..."
         *   }
         * }
         */

        /* =========================
           CPU
        ========================= */

        let cpu = Number(d.cpu_percent ?? 0);

        /*
         * Nếu backend chưa tính được CPU,
         * đọc trực tiếp từ raw.cpu
         */
        if (d.raw && d.raw.cpu) {

            const cpuMatch = d.raw.cpu.match(
                /five seconds:\s*(\d+)%\/(\d+)%/i
            );

            if (cpuMatch) {
                cpu = Number(cpuMatch[1]);
            }
        }


        /* =========================
           MEMORY
        ========================= */

        let mem = 0;

        if (d.raw && d.raw.memory) {

            /*
             * Dòng Cisco:
             *
             * Processor
             * 658B0BA0
             * 98890848
             * 17040692
             * 81850156
             *
             * Total = 98890848
             * Used  = 17040692
             */

            const memoryMatch =
                d.raw.memory.match(
                    /Processor\s+\S+\s+(\d+)\s+(\d+)\s+(\d+)/
                );

            if (memoryMatch) {

                const total =
                    Number(memoryMatch[1]);

                const used =
                    Number(memoryMatch[2]);

                if (total > 0) {

                    mem =
                        (used / total) * 100;
                }
            }
        }


        /* =========================
           TEMPERATURE
        ========================= */

        const temperature =
            d.temperature;


        /* =========================
           DISPLAY CPU
        ========================= */

        $('#cpuMetric').textContent =
            cpu.toFixed(1) + '%';


        /* =========================
           DISPLAY MEMORY
        ========================= */

        $('#memMetric').textContent =
            mem.toFixed(1) + '%';


        /* =========================
           DISPLAY TEMPERATURE
        ========================= */

        if (
            temperature !== null &&
            temperature !== undefined
        ) {

            $('#tempMetric').textContent =
                Number(temperature).toFixed(1) +
                '°C';

        } else {

            $('#tempMetric').textContent =
                'N/A';
        }


        /* =========================
           CPU BAR
        ========================= */

        $('#cpuBar').style.width =
            Math.min(cpu, 100) + '%';


        /* =========================
           MEMORY BAR
        ========================= */

        $('#memBar').style.width =
            Math.min(mem, 100) + '%';


        /* =========================
           TEMPERATURE BAR
        ========================= */

        if (
            temperature !== null &&
            temperature !== undefined
        ) {

            $('#tempBar').style.width =
                Math.min(
                    Number(temperature),
                    100
                ) + '%';

        } else {

            $('#tempBar').style.width =
                '0%';
        }


        /* =========================
           RAW OUTPUT
        ========================= */

        $('#metricRaw').textContent =
            JSON.stringify(
                d,
                null,
                2
            );

    } catch (e) {

        toast(e.message);
    }
}
async function showMetrics(n) {

    location.href =
        '/monitoring?device=' +
        encodeURIComponent(n);
}


/* =========================
   COMMAND
========================= */

async function sendCommand() {

    const n =
        $('#cmdDevice').value;

    const c =
        $('#cmdInput').value;

    if (!c) {
        return toast(
            'Nhập command'
        );
    }

    try {

        const d = await api(
            '/api/devices/' +
            encodeURIComponent(n) +
            '/command?command=' +
            encodeURIComponent(c),
            {
                method: 'POST'
            }
        );

        $('#cmdOutput').textContent =
            d.output || '';

    } catch (e) {

        $('#cmdOutput').textContent =
            e.message;
    }
}


async function showCommand(n) {

    location.href =
        '/devices?device=' +
        encodeURIComponent(n);
}


/* =========================
   RESTORE
========================= */

async function loadRestore() {

    const ds =
        await getDevices();

    $('#restoreDevice').innerHTML =
        ds.map(d => `
            <option>
                ${d.name}
            </option>
        `).join('');


    const b =
        await getBackups();

    $('#restoreFile').innerHTML =
        b
        .filter(
            x =>
                x.status === 'SUCCESS' &&
                x.path
        )
        .map(x => `
            <option value="${x.path}">
                ${x.device} — ${x.created_at}
            </option>
        `)
        .join('');
}


async function restoreSelected() {

    if (
        !confirm(
            'Xác nhận restore cấu hình lên thiết bị?'
        )
    ) {
        return;
    }

    const n =
        $('#restoreDevice').value;

    const f =
        $('#restoreFile').value;

    try {

        const d = await api(
            '/api/restore?device=' +
            encodeURIComponent(n) +
            '&backup_file=' +
            encodeURIComponent(f) +
            '&confirm=true',
            {
                method: 'POST'
            }
        );

        $('#restoreOutput').textContent =
            d.output ||
            'Restore thành công';

        toast(
            'Restore thành công'
        );

    } catch (e) {

        $('#restoreOutput').textContent =
            e.message;

        toast(e.message);
    }
}


/* =========================
   ACTIVITY
========================= */

async function loadActivity() {

    const b =
        await getBackups();

    $('#activityTable').innerHTML =
        tableBackups(b);
}


/* =========================
   GNS3
========================= */

async function loadGns3() {

    try {

        const s =
            await api('/api/gns3');

        $('#gnsStatus').textContent =
            s.success
                ? 'ONLINE'
                : 'OFFLINE';


        const p =
            await api('/api/gns3/projects');


        $('#projectCount').textContent =
            p.length;


        $('#projectsTable').innerHTML = `

            <table>

                <thead>

                    <tr>
                        <th>Project</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>

                </thead>

                <tbody>

                    ${p.map(x => `

                        <tr>

                            <td>
                                ${x.name}
                            </td>

                            <td>
                                ${x.status}
                            </td>

                            <td>

                                <button
                                    class="btn"
                                    onclick="loadNodes('${x.project_id}')">

                                    Nodes

                                </button>

                            </td>

                        </tr>

                    `).join('')}

                </tbody>

            </table>

        `;

    } catch (e) {

        toast(e.message);

        if ($('#gnsStatus')) {
            $('#gnsStatus').textContent =
                'OFFLINE';
        }
    }
}


async function loadNodes(id) {

    const n =
        await api(
            '/api/gns3/projects/' +
            id +
            '/nodes'
        );


    $('#nodesTable').innerHTML = `

        <table>

            <thead>

                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Console</th>
                </tr>

            </thead>

            <tbody>

                ${n.map(x => `

                    <tr>

                        <td>
                            ${x.name}
                        </td>

                        <td>
                            ${x.node_type}
                        </td>

                        <td>
                            ${x.status}
                        </td>

                        <td>
                            ${x.console || '-'}
                        </td>

                    </tr>

                `).join('')}

            </tbody>

        </table>

    `;
}


/* =========================
   QUERY PARAMETER
========================= */

function queryParam(k) {

    return new URLSearchParams(
        location.search
    ).get(k);
}


/* =========================
   PAGE INIT
========================= */

async function initPage() {

    activeNav();

    checkAgent();


    /* Dashboard */

    if (location.pathname === '/') {
        loadDashboard();
    }


    /* Devices */

    if (location.pathname === '/devices') {
        loadDevicesPage();
    }


    /* Backups */

    if (location.pathname === '/backups') {
        loadBackupsPage();
    }


    /* Diff */

    if (location.pathname === '/diff') {

        const q =
            queryParam('device');

        if (q) {

            setTimeout(() => {

                $('#diffDevice').value =
                    q;

                loadDiffPage();

            }, 100);

        } else {

            loadDiffPage();
        }
    }


    /* Restore */

    if (location.pathname === '/restore') {
        loadRestore();
    }


    /* Monitoring */

    if (
        location.pathname === '/monitoring'
    ) {

        const q =
            queryParam('device');

        if (q) {

            setTimeout(() => {

                $('#metricDevice').value =
                    q;

                loadMetricsPage();

            }, 100);

        } else {

            loadMetricsPage();
        }
    }


    /* Activity */

    if (
        location.pathname === '/activity'
    ) {
        loadActivity();
    }


    /* GNS3 */

    if (
        location.pathname === '/gns3'
    ) {
        loadGns3();
    }
}


/* =========================
   START
========================= */

document.addEventListener(
    'DOMContentLoaded',
    initPage
);