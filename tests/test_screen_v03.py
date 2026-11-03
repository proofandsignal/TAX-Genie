"""Static, synthetic-only regression checks for the Tax Genie public pilot.

No HTTP, Cloudflare, customer data or production tax decisions are exercised.
"""
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "site" / "taxgenie-screen-pilot"
PAGE = ROOT / "index.html"


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.in_script = True
            self.scripts.append({"attrs": dict(attrs), "body": ""})

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.scripts[-1]["body"] += data


def read_script():
    parser = ScriptParser()
    parser.feed(PAGE.read_text(encoding="utf-8"))
    for script in parser.scripts:
        src = script["attrs"].get("src", "")
        if src != "./assets/app.js":
            raise ValueError("Unexpected inline or external JavaScript")
        script["body"] = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
    return parser.scripts


class ScreenStructure(unittest.TestCase):
    def test_pilot_assets_and_no_external_integrations(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertTrue(PAGE.is_file())
        self.assertTrue((ROOT / "_headers").is_file())
        self.assertTrue((ROOT / "health.txt").is_file())
        self.assertIn("<title>Tax Genie", html)
        self.assertIn('name="robots" content="noindex,nofollow"', html)
        self.assertIn("Recoverable VAT / eligibility", html)
        self.assertIn("NOT ASSESSED", html)
        self.assertIn("No personal data, actual invoices", html)
        self.assertNotIn("<form", html)
        self.assertNotIn('type="file"', html)
        self.assertNotIn("https://cloudflareinsights.com", html)
        self.assertNotIn("fetch(", html)
        scripts = read_script()
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0]["attrs"]["src"], "./assets/app.js")
        self.assertIn('href="./assets/style.css"', html)
        self.assertNotIn("<style>", html)
        self.assertNotIn("<script>", html)
        self.assertTrue((ROOT / "assets" / "style.css").is_file())
        self.assertNotIn("unsafe-inline", (ROOT / "_headers").read_text(encoding="utf-8"))
        self.assertIn("No uploads", html)
        headers = (ROOT / "_headers").read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", headers)
        self.assertIn("connect-src 'none'", headers)
        self.assertIn("X-Robots-Tag: noindex", headers)
        self.assertTrue((ROOT / "health.txt").read_text(encoding="utf-8").startswith("TAX GENIE PILOT v0.3"))

    @unittest.skipUnless(shutil.which("node"), "Node runtime required for client-side validation")
    def test_javascript_parses(self):
        script = read_script()[0]["body"]
        result = subprocess.run(["node", "--check", "-"], input=script, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node runtime required for client-side validation")
    def test_synthetic_interactions_and_safety(self):
        script = read_script()[0]["body"]
        harness = r"""
const vm = require('node:vm');
const assert = require('node:assert/strict');
const elements = new Map();
function element(id) {
  if(!elements.has(id)) elements.set(id, {
    value:'',textContent:'',style:{},disabled:false,attributes:{},children:[],listeners:{},
    append(x){this.children.push(x)},
    addEventListener(evt,callback){this.listeners[evt]=callback},
    setAttribute(k,v){this.attributes[k]=v}
  });
  return elements.get(id);
}
const document = {getElementById:element,createElement(){return {value:'',textContent:''}}};
const context = {
 document,Intl,Date,Number,String,Array,Math,console,
 navigator:{clipboard:{writeText:async()=>{}}},window:{print(){}}
};
vm.runInNewContext(process.env.PILOT_SCRIPT + '\nwindow.qa = {model,update,validVat,summary,reset};',context,{timeout:3000});
const qa=context.window.qa;
assert.equal(qa.model().home,'DE');
assert.equal(qa.model().host,'FR');
assert.equal(qa.model().minimum,50);
assert.equal(qa.model().valid,true);
assert.equal(qa.model().amount,1200);
assert.match(element('minimum').textContent,/50/);
element('period').value='short';qa.update();
assert.equal(qa.model().minimum,400);
assert.match(element('minimum').textContent,/400/);
element('refund').value='DE';qa.update();
assert.match(element('status').textContent,/Domestic VAT route/);
element('refund').value='FR';
element('vat').value='1.123';qa.update();
assert.equal(qa.model().valid,false);
assert.equal(element('copy').disabled,true);
assert.equal(element('vat').attributes['aria-invalid'],'true');
element('vat').value='500';qa.update();
assert.equal(qa.model().valid,true);
assert.equal(element('copy').disabled,false);
element('expense').value='Fuel';qa.update();
assert.match(element('expenseStatus').textContent,/Fuel/);
assert.match(element('expenseStatus').textContent,/UNVERIFIED/);
assert.match(qa.summary(),/NOT ASSESSED/);
assert.match(qa.summary(),/SYNTHETIC RESEARCH/);
assert.doesNotMatch(qa.summary(),/Estimated recoverable VAT: €/);
qa.reset();
assert.equal(qa.model().amount,1200);
assert.equal(qa.model().period,'annual');
console.log('Synthetic screen interactions: PASS');
"""
        import os
        env = dict(os.environ, PILOT_SCRIPT=script)
        result = subprocess.run(["node", "-e", harness], env=env, text=True,
                                capture_output=True, timeout=12)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)


if __name__ == "__main__":
    unittest.main()
