import test from "node:test";import assert from "node:assert/strict";import handler,{pickHindi} from "../api/transliterate.js";
test("extracts actual provider result, never invents Devanagari",()=>{
assert.equal(pickHindi({result:{hi:["नमस्ते","नमस्त"]}}),"नमस्ते");
assert.equal(pickHindi({result:["कॉलेज"]}),"कॉलेज");
assert.throws(()=>pickHindi({result:{hi:["hello"]}}));
});
function resp(){return{code:0,headers:{},setHeader(k,v){this.headers[k]=v;return this},status(c){this.code=c;return this},json(v){this.data=v;return this},end(){return this}}}
test("rejects invalid/unwanted requests without external calls",async()=>{
for(const input of [{method:"POST",query:{word:"hi"},expected:405},{method:"GET",query:{word:"hello world"},expected:400},{method:"GET",query:{word:"मेरा"},expected:400},{method:"GET",query:{word:"x".repeat(60)},expected:400}]){
let r=resp();await handler(input,r);assert.equal(r.code,input.expected)}
});
test("real request path parses only mock upstream data (not live API)",async()=>{
const old=globalThis.fetch;globalThis.fetch=async()=>({ok:true,json:async()=>({success:true,result:{hi:["नमस्ते"]}})});
try{const r=resp();await handler({method:"GET",query:{word:"namaste"}},r);assert.equal(r.code,200);assert.equal(r.data.result,"नमस्ते");assert.equal(r.data.provider,"AI4Bharat IndicXlit hosted API")}finally{globalThis.fetch=old}
});
test("provider outage returns explicit error, not fake output",async()=>{
const old=globalThis.fetch;globalThis.fetch=async()=>{throw Error("offline")};
try{const r=resp();await handler({method:"GET",query:{word:"namaste"}},r);assert.equal(r.code,503);assert.equal(r.data.result,undefined)}finally{globalThis.fetch=old}
});
