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
function update(){const m=model();el('amount').textContent=m.valid?fmt(m.amount):'—';el('error').style.display=m.valid?'none':'block';el('vat').setAttribute('aria-invalid',m.valid?'false':'true');el('copy').disabled=!m.valid;el('route').textContent=m.home+' → '+m.host;el('minimum').textContent=m.same?'Not applicable · domestic VAT':fmt(m.minimum)+' · EU-level reference';el('threshold').textContent=m.same?'Not applicable to domestic route':!m.valid?'Invalid hypothetical VAT amount':'NOT ASSESSED · requested refund unknown';el('deadline').textContent=m.same?'Not applicable to Directive 2008/9/EC':m.deadline+' · verify current procedure';el('expenseStatus').textContent=m.expense+' · UNVERIFIED';
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
reset();
