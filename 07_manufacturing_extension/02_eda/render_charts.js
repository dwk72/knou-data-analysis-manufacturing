#!/usr/bin/env node
"use strict";
// Deterministic vector figures for the synthetic KNOU manufacturing batch case.
// Node.js standard library only; no personal, factory, or external source data.
// Execute: node 07_manufacturing_extension/02_eda/render_charts.js
// Verify committed charts: node 07_manufacturing_extension/02_eda/render_charts.js --check
const fs=require("node:fs");
const path=require("node:path");

function parseCsv(csv) {
  const lines=csv.replace(/^\uFEFF/,"").trim().split(/\r?\n/);
  const headers=lines.shift().split(",");
  const required=["batch_id","sequence","reaction_time","energy_kwh_per_ton","dq_missing_count","dq_outlier_count","dq_review_flag","quality_flag"];
  for(const field of required) if(!headers.includes(field)) throw new Error("Missing column: "+field);
  const data=lines.filter(Boolean).map(line=>Object.fromEntries(line.split(",").map((val,i)=>[headers[i],val])));
  if(data.length!==800)throw new Error("Unexpected batch count: "+data.length);
  const ids=new Set();
  for(const r of data){
    if(ids.has(r.batch_id))throw new Error("Repeated Batch ID: "+r.batch_id);
    ids.add(r.batch_id);
    for(const key of ["sequence","reaction_time","energy_kwh_per_ton","dq_missing_count","dq_outlier_count"]){
      if(r[key]===""||!Number.isFinite(Number(r[key])))throw new Error(`Invalid ${key} in ${r.batch_id}`);
      r[key]=Number(r[key]);
    }
  }
  return data.sort((a,b)=>a.sequence-b.sequence);
}

function fmt(n,d=1){return n.toFixed(d);}

function escapeXml(v){return String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}

function meanOf(rows,key){return rows.reduce((s,r)=>s+r[key],0)/rows.length;}

function makeTrend(rows,variable,title,axisLabel,step){
  const W=960,H=472,left=90,right=38,top=90,bottom=85;
  const pw=W-left-right,ph=H-top-bottom;
  const nums=rows.map(r=>r[variable]);
  const vmin=Math.floor(Math.min(...nums)/step)*step, vmax=Math.ceil(Math.max(...nums)/step)*step;
  const lo=vmin===vmax?vmin-step:vmin,hi=vmin===vmax?vmax+step:vmax;
  const x=(b)=>left+(b-1)/799*pw;
  const y=(v)=>top+ph-(v-lo)/(hi-lo)*ph;
  const raw=rows.map((r,i)=>(i===0?"M":"L")+fmt(x(r.sequence),2)+","+fmt(y(r[variable]),2)).join(" ");
  const N=40;let sum=0;const roll=[];for(let i=0;i<rows.length;i++){sum+=rows[i][variable];if(i>=N)sum-=rows[i-N][variable];if(i>=N-1)roll.push([rows[i].sequence,sum/N]);}
  const avg=roll.map((pair,i)=>(i===0?"M":"L")+fmt(x(pair[0]),2)+","+fmt(y(pair[1]),2)).join(" ");
  const early=rows.filter(r=>r.sequence<=500),late=rows.filter(r=>r.sequence>500);
  const grid=Array.from({length:Math.round((hi-lo)/step)+1},(_,i)=>lo+i*step).map(t=>`<line x1="${left}" y1="${fmt(y(t),2)}" x2="${W-right}" y2="${fmt(y(t),2)}" stroke="#E3E4EC" stroke-width="1"/><text x="${left-12}" y="${fmt(y(t)+4,2)}" text-anchor="end" fill="#697086" font-size="13">${escapeXml(fmt(t,step<1?2:0))}</text>`).join("");
  const xticks=[1,100,200,300,400,500,600,700,800].map(t=>`<line x1="${fmt(x(t),2)}" y1="${top+ph}" x2="${fmt(x(t),2)}" y2="${top+ph+6}" stroke="#A6A9B8"/><text x="${fmt(x(t),2)}" y="${top+ph+26}" fill="#697086" font-size="13" text-anchor="middle">${t}</text>`).join("");
  const marker=x(500);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${escapeXml(title)} by batch index, rolling mean and injected drift boundary">
<title>${escapeXml(title)}</title><desc>Synthetic manufacturing demonstration, 800 batches. The purple line is the trailing 40-batch rolling average. A dashed vertical marker is placed at batch 500, where drift was deliberately injected into the generator.</desc>
<rect width="100%" height="100%" fill="#FFFFFF"/><style>text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}</style>
<text x="44" y="44" fill="#242234" font-size="25" font-weight="700">${escapeXml(title)}</text>
<text x="44" y="67" fill="#616879" font-size="13">Synthetic manufacturing data, 800 batches · generated scenario, not factory observations</text>
${grid}<line x1="${left}" y1="${top+ph}" x2="${W-right}" y2="${top+ph}" stroke="#8F93A3" stroke-width="1.3"/>
<path d="${raw}" fill="none" stroke="#B5A1DF" stroke-opacity=".4" stroke-width="1" stroke-linejoin="round"/>
<line x1="${fmt(marker,2)}" y1="${top}" x2="${fmt(marker,2)}" y2="${top+ph}" stroke="#C57F46" stroke-width="1.6" stroke-dasharray="6,5"/>
<path d="${avg}" fill="none" stroke="#6236A5" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
${xticks}
<text x="${W/2}" y="${H-47}" fill="#55596D" font-size="14" text-anchor="middle">Batch sequence</text><text x="${left}" y="${H-15}" fill="#5F6374" font-size="12">${escapeXml(axisLabel)} · batches 1–500 mean ${fmt(meanOf(early,variable),2)}; 501–800 mean ${fmt(meanOf(late,variable),2)}</text>
<rect x="633" y="91" width="13" height="4" rx="1" fill="#6236A5"/><text x="652" y="98" fill="#4B5062" font-size="12">40-batch rolling mean</text>
<line x1="633" y1="114" x2="646" y2="114" stroke="#C57F46" stroke-width="2" stroke-dasharray="4,3"/><text x="652" y="119" fill="#4B5062" font-size="12">Injected drift starts (501)</text></svg>`;
}

function makeQuality(rows){
  const counts={pass:0,missingOnly:0,outlierOnly:0,both:0};
  for(const row of rows){
    const missing=row.dq_missing_count>0,outlier=row.dq_outlier_count>0;
    counts[missing&&outlier?"both":missing?"missingOnly":outlier?"outlierOnly":"pass"]++;
    if((missing||outlier)!==(row.dq_review_flag==="REVIEW")) throw new Error("Flag mismatch: "+row.batch_id);
  }
  const series=[
    ["PASS (no review flag)",counts.pass,"#68A99A"],
    ["Missing values only",counts.missingOnly,"#E9B46F"],
    ["IQR candidates only",counts.outlierOnly,"#8B67C1"],
    ["Both types",counts.both,"#BB7B8C"]
  ];
  const W=960,H=425,plotX=316,plotW=535,top=118,rowH=66;
  const guide=[0,200,400,600,800].map(t=>`<line x1="${plotX+plotW*t/800}" y1="${top-17}" x2="${plotX+plotW*t/800}" y2="${top+rowH*4-19}" stroke="#EAEBF1"/><text x="${plotX+plotW*t/800}" y="${top-29}" fill="#656A7C" font-size="12" text-anchor="middle">${t}</text>`).join("");
  const bars=series.map((s,i)=>{
    const yy=top+i*rowH;
    return `<text x="42" y="${yy+18}" fill="#3B3A4A" font-size="16">${escapeXml(s[0])}</text><rect x="${plotX}" y="${yy-2}" width="${plotW}" height="30" rx="5" fill="#F0EFF4"/><rect x="${plotX}" y="${yy-2}" width="${fmt(plotW*s[1]/800,3)}" height="30" rx="5" fill="${s[2]}"/><text x="868" y="${yy+19}" fill="#37364D" font-size="16" font-weight="700">${s[1]}</text><text x="917" y="${yy+19}" fill="#666B7A" font-size="12" text-anchor="end">${fmt(100*s[1]/800,1)}%</text>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Quality review classifications for 800 synthetic manufacturing batches">
<title>Data quality review categories</title><desc>717 passes, 22 missing-only batches, 59 IQR-outlier-only batches, and 2 with both conditions. IQR candidate is not a confirmed manufacturing defect.</desc>
<rect width="100%" height="100%" fill="#FFFFFF"/><style>text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}</style>
<text x="42" y="45" font-size="25" font-weight="700" fill="#242234">Data quality review categories</text>
<text x="42" y="72" font-size="14" fill="#606778">Synthetic manufacturing data · 83 REVIEW / 800 batches (10.4%)</text>
${guide}${bars}
<text x="42" y="406" fill="#6A6C7D" font-size="13">IQR outlier means “review candidate”; it does not mean defective product or bad measurement.</text>
</svg>`;
}

function makeAll(rows){
 const figures={
   "reaction_time_by_batch.svg":makeTrend(rows,"reaction_time","Reaction time across batches","Reaction time (synthetic scale)",5),
   "energy_intensity_by_batch.svg":makeTrend(rows,"energy_kwh_per_ton","Energy intensity across batches","Energy intensity (synthetic kWh/t)",10),
   "data_quality_review.svg":makeQuality(rows)
 };
 if(Object.keys(figures).length!==3||Object.values(figures).some(s=>!s.includes("<svg")||!s.includes("</svg>")))throw new Error("SVG render failed");
 return figures;
}
function main(){
  const project=path.resolve(__dirname,"..");
  const input=path.join(project,"01_data_integration","output","integrated_master.csv");
  const output=path.join(__dirname,"figures");
  const rows=parseCsv(fs.readFileSync(input,"utf8"));
  const figures=makeAll(rows);
  const check=process.argv.includes("--check");
  if(!check)fs.mkdirSync(output,{recursive:true});
  for(const [filename,content] of Object.entries(figures)){
    const filePath=path.join(output,filename);
    if(check){
      if(!fs.existsSync(filePath)||fs.readFileSync(filePath,"utf8")!==content)
        throw new Error("Chart missing or stale: "+filePath);
      console.log("PASS verified "+filename);
    }else{
      fs.writeFileSync(filePath,content,"utf8");
      console.log("Wrote "+filePath);
    }
  }
}
if(require.main===module)main();
module.exports={parseCsv,makeAll};
