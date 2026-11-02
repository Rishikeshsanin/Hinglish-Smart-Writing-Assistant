const UPSTREAM="https://xlit-api.ai4bharat.org/tl/hi/";
const WORD=/^[A-Za-z]{1,40}$/;

export function pickHindi(payload) {
  const result=payload?.result;
  const candidates=Array.isArray(result)?result:result?.hi;
  if (!Array.isArray(candidates)) throw new Error("Unexpected upstream format");
  const selected=candidates.find(s=>typeof s==="string"&&s.trim());
  if(!selected||!/[\u0900-\u097f]/u.test(selected))throw new Error("No Devanagari suggestion from upstream");
  return selected;
}

export default async function handler(req,res) {
  res.setHeader("Cache-Control","private, no-store");
  res.setHeader("X-Content-Type-Options","nosniff");
  res.setHeader("Access-Control-Allow-Origin","*");
  res.setHeader("Access-Control-Allow-Methods","GET, OPTIONS");
  if(req.method==="OPTIONS")return res.status(204).end();
  if(req.method!=="GET")return res.status(405).json({error:"Only GET supported"});
  const raw=req.query?.word;
  if(typeof raw!=="string"||!WORD.test(raw))return res.status(400).json({error:"Expected one alphabetic Roman token (1–40 characters)"});
  try{
    const response=await fetch(UPSTREAM+encodeURIComponent(raw),{
      method:"GET",headers:{Accept:"application/json"},signal:AbortSignal.timeout(8000)
    });
    if(!response.ok)throw new Error("Upstream unavailable");
    const data=await response.json();
    if(data?.success===false)throw new Error("Upstream declined request");
    return res.status(200).json({word:raw,result:pickHindi(data),provider:"AI4Bharat IndicXlit hosted API"});
  }catch(err){
    return res.status(503).json({error:"The official AI4Bharat hosted service is currently unavailable. Try again later; no synthetic result is substituted."});
  }
}
