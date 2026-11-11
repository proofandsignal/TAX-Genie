'use strict';
const countries=[['AT','Austria'],['BE','Belgium'],['BG','Bulgaria'],['HR','Croatia'],['CY','Cyprus'],['CZ','Czechia'],['DK','Denmark'],['EE','Estonia'],['FI','Finland'],['FR','France'],['DE','Germany'],['GR','Greece'],['HU','Hungary'],['IE','Ireland'],['IT','Italy'],['LV','Latvia'],['LT','Lithuania'],['LU','Luxembourg'],['MT','Malta'],['NL','Netherlands'],['PL','Poland'],['PT','Portugal'],['RO','Romania'],['SK','Slovakia'],['SI','Slovenia'],['ES','Spain'],['SE','Sweden']];
const el=id=>document.getElementById(id);
const fmt=n=>new Intl.NumberFormat('en-IE',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2}).format(n);
for(const id of ['est','refund']){for(const [code,name] of countries){const opt=document.createElement('option');opt.value=code;opt.textContent=name+' ('+code+')';el(id).append(opt);}}
const currentYear=new Date().getFullYear();
for(let year=Math.max(2024,currentYear-2);year<=currentYear+1;year++){const opt=document.createElement('option');opt.value=String(year);opt.textContent=String(year)+(year>currentYear?' · planning':'');el('year').append(opt);}
function reset(){el('est').value='DE';el('refund').value='FR';el('year').value=String(currentYear);el('period').value='annual';el('vat').value='1200';el('expense').value='Accommodation';el('deduction').value='unknown';el('established').value='unknown';el('supplies').value='unknown';el('feedback').textContent='';update();}
function validVat(raw){if(!raw||!raw.trim()||!/^\d+(?:\.\d{1,2})?$/.test(raw.trim()))return false;const v=Number(raw);return Number.isFinite(v)&&v>=0&&v<=10000000;}
function model(){const home=el('est').value,host=el('refund').value,year=Number(el('year').value),period=el('period').value,raw=el('vat').value;const valid=validVat(raw),amount=valid?Number(raw):null;const same=home===host,minimum=period==='short'?400:50;const deadline='30 Sep '+(year+1);const expired=Date.now()>=Date.UTC(year+1,9,1);const uncertain=['deduction','established','supplies'].some(id=>el(id).value==='unknown');const statusRisk=el('deduction').value==='no'||el('established').value==='yes'||el('supplies').value==='yes';return {home,host,year,period,valid,amount,same,minimum,deadline,expired,uncertain,statusRisk,expense:el('expense').value};}
function update(){const m=model();el('amount').textContent=m.valid?fmt(m.amount):'—';el('error').style.display=m.valid?'none':'block';el('vat').setAttribute('aria-invalid',m.valid?'false':'true');el('copy').disabled=!m.valid;el('brief-copy').disabled=!m.valid;el('brief-print').disabled=!m.valid;el('print').disabled=!m.valid;el('route').textContent=m.home+' → '+m.host;el('minimum').textContent=m.same?'Not applicable · domestic VAT':fmt(m.minimum)+' · EU-level reference';el('threshold').textContent=m.same?'Not applicable to domestic route':!m.valid?'Invalid hypothetical VAT amount':'NOT ASSESSED · requested refund unknown';el('deadline').textContent=m.same?'Not applicable to Directive 2008/9/EC':m.deadline+' · verify current procedure';el('expenseStatus').textContent=m.expense+' · UNVERIFIED';
let label='Cross-border research pathway · eligibility not assessed',warn=false;
if(m.same){label='Domestic VAT route · EU cross-border refund procedure not applicable';warn=true;}
else if(!m.valid){label='Enter a valid fictional VAT amount for the research scenario';warn=true;}
else if(m.expired){label='General filing deadline has passed for this period';warn=true;}
else if(m.statusRisk){label='Possible business-status restriction · human review required';warn=true;}

const details=['VAT figures are amounts charged, not requested or predicted refunds.','The €50 / €400 thresholds apply to the total VAT requested in an application, not the VAT charged shown here. No application amount is calculated.','National restrictions and category rules are NOT VERIFIED.'];
if(m.uncertain)details.push('Business status assumptions remain unknown.');
if(m.statusRisk)details.push('Potentially disqualifying business status requires professional evaluation; exceptions are not assessed.');
if(m.expired)details.push('No deadline exceptions or alternative procedures are validated here.');
details.push(m.period==='short'?'€400 is the requested-refund minimum for a qualifying 3–11-month period. Exact start/end months are not collected or checked.':'€50 is the requested-refund minimum for a full calendar year or the genuine remainder of a calendar year. Exact dates are not checked.');
if(m.home!=='DE'||m.host!=='FR')details.push('This route has no validated national rules; country-specific currency equivalents may apply.');
if(m.home==='DE'&&m.host==='FR')details.push('Germany → France is an initial research focus, not a validated French rule pack.');
el('status').textContent=label;el('status').className='status'+(warn?' warn':'');el('details').textContent=details.join(' ');
  syncBrief();
  renderFindings(m);
}
function summary(){const m=model();if(!m.valid)return '';return ['TAX GENIE · SYNTHETIC RESEARCH SUMMARY v0.3','Scenario (fictional): '+m.home+' → '+m.host,'Period: '+m.year+' / '+m.period,'Hypothetical VAT charged: '+fmt(m.amount),'General EU minimum requested refund: '+(m.same?'not applicable':fmt(m.minimum)),'General filing deadline: '+(m.same?'not applicable':m.deadline),'Minimum comparison: NOT ASSESSED (charged VAT is not the requested refund amount)','Expense category: '+m.expense+' (country rules NOT VERIFIED)','Screen message: '+el('status').textContent,'Recoverable VAT: NOT ASSESSED','Eligibility: UNDETERMINED','No real invoices or business data entered. Not tax/legal advice.','Legal basis reference: https://eur-lex.europa.eu/eli/dir/2008/9/oj'].join('\n');}
el('copy').addEventListener('click',async()=>{try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw new Error('clipboard unavailable');await navigator.clipboard.writeText(summary());el('feedback').textContent='Synthetic summary copied. Verify content before sharing.';}catch(_){el('feedback').textContent='Copy unavailable. Use Print to save a synthetic summary.';}});
el('reset').addEventListener('click',reset);el('print').addEventListener('click',()=>window.print());
for(const id of ['est','refund','period','year','vat','expense','deduction','established','supplies']){el(id).addEventListener('input',update);el(id).addEventListener('change',update);}
// Presets exist only in this browser tab; they are not tracked or sent.
document.querySelectorAll('[data-preset]').forEach(button=>{
  button.addEventListener('click',()=>{
    const preset=button.getAttribute('data-preset');
    if(preset==='de-fr'){
      el('est').value='DE';el('refund').value='FR';el('period').value='annual';el('vat').value='1200';el('expense').value='Accommodation';
    }else if(preset==='fr-de'){
      el('est').value='FR';el('refund').value='DE';el('period').value='short';el('vat').value='350';el('expense').value='Trade fairs';
    }else if(preset==='domestic'){
      el('est').value='DE';el('refund').value='DE';el('period').value='annual';el('vat').value='1200';el('expense').value='Accommodation';
    }else{return;}
    el('year').value=String(currentYear);
    el('deduction').value='unknown';el('established').value='unknown';el('supplies').value='unknown';
    update();
    el('feedback').textContent='Fictional sample loaded. No refund assessment performed.';
    el('explore').scrollIntoView({behavior:'auto',block:'start'});
  });
});

// Evidence Vault is a visual learning checklist; checked means question explored,
// not verified or satisfied. This is not a real-dossier workflow.
function exploredCount(){return [...document.querySelectorAll('[data-evidence]')].filter(x=>x.checked).length;}
function updateEvidence(){
 const n=exploredCount();
 el('evidence-count').textContent=n+' / 6';
 el('brief-evidence').textContent=n+' of 6 (demo only)';
 el('progress-fill').style.width=(n/6*100)+'%';
 el('progressbar').setAttribute('aria-valuenow',String(n));
}
for(const checkbox of document.querySelectorAll('[data-evidence]')){
 checkbox.addEventListener('change',updateEvidence);
}
el('evidence-reset').addEventListener('click',()=>{
 for(const checkbox of document.querySelectorAll('[data-evidence]')) checkbox.checked=false;
 updateEvidence();
});

/**
 * Non-advisory research prompts generated from synthetic UI selections only.
 * They are not tax conclusions; no country-specific rule is inferred.
 */
function getResearchFindings(m){
 const flags=[];
 const add=(kind,title,reason,next)=>flags.push({kind,title,reason,next});
 if(!m.valid) add('stop','Invalid sample amount','A fictional amount must be a non-negative EUR number with at most two decimals.','Correct the demo input before copying a report.');
 if(m.same) add('stop','Domestic route, different process','The cross-border research procedure in Directive 2008/9/EC is not the procedure to assess this same-country scenario.','Investigate the relevant domestic procedure separately; not evaluated here.');
 else add('info','Research framework identified','This is a hypothetical EU establishment-to-refund-country route. The selected national rules are not validated.','Verify both states, taxable-person status and local rules with official sources.');
 if(m.expired) add('stop','General EU filing date has passed','The reference 30 September deadline after the chosen period is in the past. Exceptions and other procedures have not been assessed.','Obtain qualified advice on the relevant deadlines and any lawful alternatives.');
 else if(m.year>currentYear) add('review','Future hypothetical period','The selected period is in the future. The screen does not forecast future rules or acceptance.','Recheck applicable rules and dates when the period is known.');
 if(m.period==='short') add('review','Exact 3–11 months are unverified','The UI selects a period category, but does not ask for the precise beginning/end dates.','Verify exact period dates before relying on a minimum or deadline.');
 if(m.period==='remainder') add('review','Remainder-year classification unverified','The UI does not establish that the period is the permitted final remainder of a calendar year.','Check exact dates, scope, and the general framework in Article 16.');
 const established=el('established').value, supplies=el('supplies').value, deduction=el('deduction').value;
 if(established==='yes'||supplies==='yes'||deduction==='no')add('stop','Business status requires human review','A selected establishment, local supply, or deduction-right assumption could affect which tax process applies. Exceptions are not assessed.','Have a qualified expert validate the facts and national procedure.');
 else if(m.uncertain)add('review','Business eligibility facts unknown','One or more taxable-person, deduction-right, or local activity assumptions have not been verified.','Collect authoritative status evidence outside this demo; do not upload actual documents here.');
 add('review','Expense category requires national rules',m.expense+' is the selected fictional expense type. Tax Genie has no validated '+m.host+' expense-eligibility rule pack.','Seek current national guidance and qualified professional review.');
 add('info','Requested refund cannot be calculated','The EUR amount is VAT charged, not the refund amount requested. The €50/€400 references apply to a claim/request amount, which is not calculated here.','Do not infer threshold pass, eligibility or recoverable VAT from this screen.');
 add('review','Invoice evidence not examined','The research pilot accepts no invoices, VAT identifiers, or real client records.','Use an approved secure intake only after privacy, security and methodology review.');
 return flags;
}
function renderFindings(m){
 const cards=getResearchFindings(m);
 const grid=el('signal-grid');
 grid.textContent='';
 for(const flag of cards){
  const card=document.createElement('article');
  card.className='signal-card signal-'+flag.kind;
  const tag=document.createElement('span');
  tag.className='signal-type';tag.textContent=flag.kind==='stop'?'PROCEDURE / INPUT FLAG':flag.kind==='info'?'EU FRAMEWORK / REFERENCE':'REQUIRES VERIFICATION';
  const title=document.createElement('strong');title.textContent=flag.title;
  const reason=document.createElement('p');reason.textContent=flag.reason;
  const next=document.createElement('small');next.textContent='NEXT RESEARCH STEP · '+flag.next;
  card.append(tag,title,reason,next);
  grid.append(card);
 }
 const critical=cards.filter(x=>x.kind==='stop').length;
 el('brief-flags').textContent=cards.length+' synthetic research prompts · '+critical+' procedure/input flags · not an eligibility verdict';
 el('brief-action').textContent=cards.find(x=>x.kind==='stop')?.next||cards.find(x=>x.kind==='review')?.next||'Review current primary sources with a qualified specialist.';
}

function syncBrief(){
 const m=model();
 el('brief-route').textContent=m.home+' → '+m.host;
 el('brief-period').textContent=m.year+' / '+(m.period==='short'?'3–11-month category':m.period==='remainder'?'Year remainder':'Calendar year');
 el('brief-vat').textContent=m.valid?fmt(m.amount):'INVALID / FICTIONAL INPUT';
 el('brief-signal').textContent=el('status').textContent;
}
el('brief-copy').addEventListener('click',async()=>{
 const n=exploredCount();
 const core=summary();
 const findings=getResearchFindings(model()).map((x,i)=>(i+1)+'. '+x.title+' — '+x.reason+' NEXT: '+x.next).join('\n');
 const brief=core+'\n\nRESEARCH PROMPTS (NOT VERIFIED):\n'+findings+'\n\nDemo questions explored: '+n+' of 6 (NOT verified)\nVAT refund forecast: NONE\nIndependent legal assessment: NOT PERFORMED';
 try{
  if(!core)throw new Error('Invalid fictional amount');
  if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
  await navigator.clipboard.writeText(brief);
  el('brief-feedback').textContent='Sample dossier copied; no real client data included.';
 }catch(_){el('brief-feedback').textContent=model().valid?'Copy unavailable. Use Print to save the fictional sample.':'Correct the fictional VAT amount before exporting a dossier.';}
});
el('brief-print').addEventListener('click',()=>window.print());
const serviceData={
 mapping:{
  stage:'DISCOVERY PILOT / RESEARCH ONLY',
  title:'Trace the route. See the unknowns.',
  description:'Explore whether a hypothetical EU cross-border expense belongs in a particular research pathway. Surface the next questions without asserting VAT recovery eligibility.',
  output:'A route summary with visible decision gaps and official reference links.'
 },
 evidence:{
  stage:'PROTOTYPE / NO CLIENT DOCUMENTS',
  title:'Transform questions into an evidence map.',
  description:'Discover the documentation, status and classification questions a team would need to resolve before seeking professional VAT advice. The live pilot accepts no real invoices.',
  output:'A fictional evidence checklist and human-review handoff brief.'
 },
 rules:{
  stage:'DESIGN ONLY / NOT AN ACTIVE MONITOR',
  title:'Watch the rules. Keep the provenance.',
  description:'Concept for tracking official changes, effective dates and source evidence across EU and national VAT frameworks. No live country rule watch is operating in this preview.',
  output:'An illustrative rule-change evidence trail; implementation requires a verified source registry.'
 },
 handoff:{
  stage:'FUTURE / PARTNER VALIDATION',
  title:'Give specialists the context, not assumptions.',
  description:'Proposed handoff from business research to an independently qualified tax professional, with clear unanswered questions and source references. No partner or filing capability is represented as active.',
  output:'A proposed client-to-expert research brief and review queue.'
 }
};
for(const button of document.querySelectorAll('[data-service]')){
 button.addEventListener('click',()=>{
  const key=button.getAttribute('data-service'),item=serviceData[key];
  if(!item)return;
  for(const b of document.querySelectorAll('[data-service]')){
   const chosen=b===button;
   b.className='service-choice'+(chosen?' active':'');
   b.setAttribute('aria-pressed',chosen?'true':'false');
  }
  el('service-stage').textContent=item.stage;
  el('service-title').textContent=item.title;
  el('service-description').textContent=item.description;
  el('service-output').textContent=item.output;
 });
}
updateEvidence();

reset();
