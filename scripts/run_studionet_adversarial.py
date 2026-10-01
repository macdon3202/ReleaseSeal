"""Create one releasable record, then prove wrong-integrity rollback and malformed-input rollback."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

RPC="https://studio.genlayer.com/api"; EX="https://explorer-studio.genlayer.com"
ROOT=Path(__file__).resolve().parents[1]
BASE="9f0a3d81221e3ab7c09ca4911ef35b54817869a4"; HEAD="f300476db2942180206a08af2f093534adfbdffa"

def load():
    for raw in (ROOT.parent/"secrets"/"genlayer-test-wallets.env").read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            k,v=raw.split("=",1);os.environ.setdefault(k.strip(),v.strip().strip("'\"").strip("<>"))
def plain(v):
    if isinstance(v,dict):return {str(k):plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [plain(x) for x in v]
    return v if isinstance(v,(str,int,float,bool)) or v is None else str(v)
def read(c,a,w,m,args):return plain(c.read_contract(address=a,function_name=m,args=args,account=w))
def sig(info):
    status=str(info.get("status_name") or info.get("status") or "").upper();cons=str(info.get("result_name") or info.get("consensus_result") or "").upper();d=info.get("consensus_data") or {};rs=d.get("leader_receipt") or d.get("validators") or [];rs=[rs] if isinstance(rs,dict) else rs;l=next((x for x in rs if str(x.get("mode","")).lower()=="leader"),rs[0] if rs else {});exe=str(l.get("execution_result") or "").upper();res=l.get("result") or {};return status,cons,exe,res.get("payload","") if isinstance(res,dict) else ""
def send(c,a,w,m,args,success):
    tx=str(c.write_contract(address=a,function_name=m,account=w,args=args,value=0));print(json.dumps({"submitted":tx,"method":m}),flush=True)
    for _ in range(240):
        s,co,e,r=sig(plain(c.get_transaction(tx)))
        if s=="FINALIZED":
            ok=co in {"MAJORITY_AGREE","AGREE","ACCEPTED"} and e=="SUCCESS"
            if ok!=success:raise AssertionError((s,co,e,r,tx))
            return {"hash":tx,"url":f"{EX}/tx/{tx}","status":s,"consensus":co,"execution":e,"reason":r}
        time.sleep(3)
    raise TimeoutError(tx)
def main():
    if len(sys.argv)!=2:raise SystemExit("usage: run_studionet_adversarial.py ADDRESS")
    address=sys.argv[1];load();a=create_account(os.environ["SERVICE_LEDGER_KEY_A"]);b=create_account(os.environ["SERVICE_LEDGER_KEY_B"]);c=create_client(chain=studionet,account=a,endpoint=RPC)
    args=["colinhacks","zod",BASE,HEAD,"zod","4.5.0-canary.20260817T183748","packages/zod/src/v4/core","packages/zod/src/v4/classic/tests"]
    before_count=read(c,address,a,"get_config",[]);reg=send(c,address,a,"register_release",args,True);rid=int(read(c,address,a,"get_config",[])["release_count"]);ins=send(c,address,b,"inspect_release",[rid],True);record=read(c,address,b,"get_release",[rid])
    if record["state"]!="RELEASABLE":raise AssertionError(record)
    pre=record;wrong=send(c,address,b,"activate_release",[rid,"sha512-attacker-controlled"],False);post=read(c,address,a,"get_release",[rid])
    if pre!=post:raise AssertionError("WRONG_INTEGRITY_MUTATED_STATE")
    pre_cfg=read(c,address,a,"get_config",[]);malformed=send(c,address,b,"register_release",["colinhacks","zod",BASE,"bad","zod","4.5.0","src","tests"],False);post_cfg=read(c,address,a,"get_config",[])
    if pre_cfg!=post_cfg:raise AssertionError("MALFORMED_INPUT_MUTATED_STATE")
    out={"contract":address,"wallets":{"a":str(a.address),"b":str(b.address)},"setup":{"register":reg,"inspect":ins,"release":record},"wrong_integrity":{"transaction":wrong,"pre":pre,"post":post},"malformed_head":{"transaction":malformed,"pre_config":pre_cfg,"post_config":post_cfg},"initial_config":before_count}
    (ROOT/"docs"/"studionet-adversarial.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8");print(json.dumps(out,indent=2))
if __name__=="__main__":main()
