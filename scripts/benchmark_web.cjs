// No extra npm dependencies: drive a local Chromium through its CDP WebSocket.
const { spawn } = require('node:child_process');
const { mkdir, writeFile, mkdtemp, rm } = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');

async function main() {
  const label = process.argv[2] || 'optimized';
  const width = Number(process.env.BENCH_WIDTH || 1280);
  const height = Number(process.env.BENCH_HEIGHT || 720);
  const dpr = Number(process.env.BENCH_DPR || (label === 'smoke' ? 2 : 1));
  const query = process.env.BENCH_QUERY || (label === 'baseline' ? 'baseline' : '');
  const baseURL = process.env.BENCH_BASE_URL || 'http://127.0.0.1:5173/';
  const dir = path.resolve('assets/analysis/web-performance');
  await mkdir(dir, { recursive: true });
  const profile = await mkdtemp(path.join(os.tmpdir(), 'apt-perf-'));
  const port = await new Promise((resolve, reject) => {
    const server = require('node:net').createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
  const executable = process.env.BROWSER_EXECUTABLE || path.join(os.homedir(), 'AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe');
  const browser = spawn(executable, [
    '--headless=new', '--no-first-run', '--no-default-browser-check',
    '--disable-background-networking', '--disable-extensions',
    `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, 'about:blank',
  ], { windowsHide: true, stdio: 'ignore' });
  let ws;
  try {
    let targets;
    for (let i = 0; i < 100; i++) {
      try { targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); break; }
      catch { await new Promise(r => setTimeout(r, 100)); }
    }
    if (!targets) throw Error('Chromium CDP failed to start');
    ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    let id = 0;
    const pending = new Map();
    const errors = [];
    ws.onmessage = ({ data }) => {
      const event = JSON.parse(data);
      if (event.id) {
        const p = pending.get(event.id); pending.delete(event.id);
        if (event.error) p.reject(Error(JSON.stringify(event.error))); else p.resolve(event.result);
      } else if (event.method === 'Runtime.exceptionThrown') errors.push(event.params.exceptionDetails);
      else if (event.method === 'Runtime.consoleAPICalled' && event.params.type === 'error') {
        errors.push({ consoleError: event.params.args.map(arg => arg.value ?? arg.description).join(' ') });
      }
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      const next = ++id; pending.set(next, { resolve, reject }); ws.send(JSON.stringify({ id: next, method, params }));
    });
    const evaluate = async expression => {
      const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
      if (r.exceptionDetails) throw Error(JSON.stringify(r.exceptionDetails));
      return r.result.value;
    };
    await send('Runtime.enable');
    if (process.env.BENCH_MAIN === '1') {
      const report = { url: baseURL, views: [], errors };
      // One viewport per process: repeated high-DPR reloads can exhaust GPU contexts.
      for (const [mainWidth, mainHeight, mainDpr] of [[width, height, dpr]]) {
        await send('Emulation.setDeviceMetricsOverride', { width: mainWidth, height: mainHeight, deviceScaleFactor: mainDpr, mobile: false });
        await send('Page.navigate', { url: baseURL });
        for (let i = 0; i < 600; i++) {
          if (errors.length) throw Error(JSON.stringify(errors));
          if (await evaluate("document.querySelector('#loader')?.style.display === 'none' && !!document.querySelector('#pos')?.textContent")) break;
          await new Promise(r => setTimeout(r, 250));
          if (i === 599) throw Error('Main page timeout');
        }
        const state = await evaluate(`(async()=>{
          for(let i=0;i<60;i++)await new Promise(requestAnimationFrame);
          const canvas=document.querySelector('#scene');const gl=canvas.getContext('webgl2');
          const ext=gl.getExtension('WEBGL_debug_renderer_info');
          const values=[];let previous=await new Promise(requestAnimationFrame);
          const walk=${process.env.BENCH_WALK === '1'};if(walk)window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyW'}));
          for(let i=0;i<180;i++){if(walk&&i===90){window.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyW'}));window.dispatchEvent(new KeyboardEvent('keydown',{code:'KeyS'}));}const t=await new Promise(requestAnimationFrame);values.push(t-previous);previous=t;}
          if(walk)window.dispatchEvent(new KeyboardEvent('keyup',{code:'KeyS'}));
          if(gl.isContextLost())throw Error('WebGL context lost; performance result is invalid');
          values.sort((a,b)=>a-b);
          return {drawingBuffer:[canvas.width,canvas.height],gpu:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,
            meanFps:1000/(values.reduce((a,b)=>a+b,0)/values.length),medianMs:values[90],p95Ms:values[171]};
        })()`);
        if (errors.length) throw Error(JSON.stringify(errors));
        report.views.push({ width: mainWidth, height: mainHeight, dpr: mainDpr, ...state });
        console.log(JSON.stringify(report.views.at(-1)));
      }
      await writeFile(path.join(dir, `${label}.json`), JSON.stringify(report, null, 2) + '\n');
      return;
    }
    await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: dpr, mobile: false });
    if (label === 'smoke') {
      await send('Page.navigate', { url: baseURL });
      for (let i = 0; i < 600; i++) {
        if (await evaluate("document.querySelector('#loader')?.style.display === 'none' && !!document.querySelector('#pos')?.textContent")) break;
        if (errors.length) throw Error(JSON.stringify(errors));
        await new Promise(r => setTimeout(r, 250));
        if (i === 599) throw Error('Main page timeout');
      }
      const settle = () => evaluate('(async()=>{for(let i=0;i<15;i++)await new Promise(requestAnimationFrame)})()');
      const capture = async name => {
        await settle();
        const shot = await send('Page.captureScreenshot', { format: 'png' });
        await writeFile(path.join(dir, `${process.env.BENCH_PREFIX || 'smoke'}-${name}.png`), Buffer.from(shot.data, 'base64'));
      };
      await capture('walk');
      await evaluate("document.querySelector('#btn-over').click()");
      await capture('overview');
      if (await evaluate("document.querySelector('#mode-label').textContent") !== '전체 보기') throw Error('Overview mode failed');
      await evaluate("document.querySelector('#btn-walk').click()");
      await capture('walk-restored');
      if (await evaluate("document.querySelector('#mode-label').textContent") !== '걷기') throw Error('Walk mode failed');
      const before = await evaluate("document.querySelector('#pos').textContent");
      await send('Input.dispatchKeyEvent', { type: 'keyDown', code: 'KeyW', key: 'w', windowsVirtualKeyCode: 87 });
      await settle();
      await send('Input.dispatchKeyEvent', { type: 'keyUp', code: 'KeyW', key: 'w', windowsVirtualKeyCode: 87 });
      const after = await evaluate("document.querySelector('#pos').textContent");
      if (before === after) throw Error('Walking did not move the player');
      await evaluate("document.querySelector('#btn-reset').click()");
      await settle();
      const reset = await evaluate("document.querySelector('#pos').textContent");
      if (before !== reset) throw Error('Reset failed');
      if (errors.length) throw Error(JSON.stringify(errors));
      const report = { viewport: `${width}x${height} DPR${dpr}`, before, after, reset, modeTransitions: 'walk -> overview -> walk', errors };
      await writeFile(path.join(dir, `${process.env.BENCH_PREFIX || 'smoke'}.json`), JSON.stringify(report, null, 2) + '\n');
      console.log(JSON.stringify(report));
      return;
    }
    await send('Page.navigate', { url: new URL(`tests/performance-review.html?${query}&dpr=${dpr}`, baseURL).href });
    for (let i = 0; i < 600; i++) {
      if (await evaluate('!!window.review')) break;
      if (errors.length) throw Error(JSON.stringify(errors));
      await new Promise(r => setTimeout(r, 250));
      if (i === 599) throw Error('Review page timeout');
    }
    const report = { label, viewport: `${width}x${height} DPR${dpr}`, query, renderer: await evaluate('window.review.renderer'), views: {} };
    for (const name of ['foyer', 'living', 'bath', 'overview']) {
      report.views[name] = await evaluate(`window.review.view('${name}', ${Number(process.env.BENCH_FRAMES || 180)})`);
      const shot = await send('Page.captureScreenshot', { format: 'png' });
      await writeFile(path.join(dir, `${label}-${name}.png`), Buffer.from(shot.data, 'base64'));
      console.log(name, JSON.stringify(report.views[name]));
      if (errors.length) throw Error(JSON.stringify(errors));
    }
    report.errors = errors;
    report.stats = await evaluate('window.review.stats');
    await writeFile(path.join(dir, `${label}.json`), JSON.stringify(report, null, 2) + '\n');
    console.log('renderer:', report.renderer);
  } finally {
    if (ws) ws.close();
    if (browser.exitCode === null) {
      const exited = new Promise(resolve => browser.once('exit', resolve));
      if (process.platform === 'win32') {
        await new Promise(resolve => {
          const killer = spawn('taskkill', ['/PID', String(browser.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' });
          killer.once('exit', resolve);
        });
      } else browser.kill();
      await exited;
    }
    const expectedPrefix = path.resolve(os.tmpdir(), 'apt-perf-');
    if (!path.resolve(profile).startsWith(expectedPrefix)) throw Error('Unexpected temporary profile path');
    await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
  }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
