import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { get } from "node:http";

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const outDir = "submission_assets/screenshots";
const port = 9223;
const userDataDir = "D:/Projects/conflictsense/.tmp-chrome-screens";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function httpJson(url) {
  return new Promise((resolve, reject) => {
    get(url, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => resolve(JSON.parse(body)));
    }).on("error", reject);
  });
}

async function connect() {
  const targets = await httpJson(`http://127.0.0.1:${port}/json/list`);
  const pageTarget = targets.find((target) => target.type === "page");
  if (!pageTarget) throw new Error("No Chrome page target found");
  const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
  await new Promise((resolve) => ws.addEventListener("open", resolve, { once: true }));
  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (event) => {
    const msg = JSON.parse(event.data.toString());
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(msg.error.message));
      else resolve(msg.result);
    }
  });
  return {
    send(method, params = {}) {
      const msgId = ++id;
      ws.send(JSON.stringify({ id: msgId, method, params }));
      return new Promise((resolve, reject) => pending.set(msgId, { resolve, reject }));
    },
    close() {
      ws.close();
    },
  };
}

async function evalJs(cdp, expression) {
  return cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
}

async function screenshot(cdp, name) {
  const result = await cdp.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
  });
  await writeFile(`${outDir}/${name}.png`, Buffer.from(result.data, "base64"));
}

async function main() {
  await mkdir(outDir, { recursive: true });
  await rm(userDataDir, { recursive: true, force: true });

  const chrome = spawn(chromePath, [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--window-size=1440,1000",
    "--disable-gpu",
    "about:blank",
  ], { stdio: "ignore" });

  try {
    for (let i = 0; i < 30; i++) {
      try {
        await httpJson(`http://127.0.0.1:${port}/json/version`);
        break;
      } catch {
        await sleep(250);
      }
    }

    const cdp = await connect();
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Page.navigate", { url: "http://127.0.0.1:5173" });
    await sleep(1500);
    await screenshot(cdp, "01_idle_state");

    await evalJs(cdp, `document.querySelector('#btn-run-analysis')?.click()`);
    await sleep(250);
    await screenshot(cdp, "02_analysis_running");
    await sleep(2500);
    await screenshot(cdp, "03_conflict_detected");

    await evalJs(cdp, `
      [...document.querySelectorAll('button, [role="button"], div')]
        .find((el) => /impact|affected/i.test(el.textContent || ''))?.scrollIntoView({block:'center'});
    `);
    await sleep(300);
    await screenshot(cdp, "05_impact_assessment");

    await evalJs(cdp, `
      [...document.querySelectorAll('button, [role="button"], div')]
        .find((el) => /risk|critical/i.test(el.textContent || ''))?.scrollIntoView({block:'center'});
    `);
    await sleep(300);
    await screenshot(cdp, "06_risk_quantification");

    await evalJs(cdp, `
      [...document.querySelectorAll('button, [role="button"], div')]
        .find((el) => /resolution|remediation/i.test(el.textContent || ''))?.scrollIntoView({block:'center'});
    `);
    await sleep(300);
    await screenshot(cdp, "07_resolution_recommendation");

    await screenshot(cdp, "08_human_approval_gate");

    await evalJs(cdp, `
      [...document.querySelectorAll('button')]
        .find((button) => /reject/i.test(button.textContent || ''))?.click();
    `);
    await sleep(500);
    await screenshot(cdp, "04_conflict_rejected");

    await evalJs(cdp, `
      [...document.querySelectorAll('button')]
        .find((button) => /approve/i.test(button.textContent || ''))?.click();
    `);
    await sleep(500);
    await screenshot(cdp, "09_remediation_workflow");

    await evalJs(cdp, `
      [...document.querySelectorAll('div, span')]
        .find((el) => /mock mode|fallback/i.test(el.textContent || ''))?.scrollIntoView({block:'center'});
    `);
    await sleep(300);
    await screenshot(cdp, "10_fallback_mode");

    cdp.close();
  } finally {
    chrome.kill();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
