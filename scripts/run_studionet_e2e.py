"""Execute ReleaseSeal live paths from two auxiliary, non-deployer wallets."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

RPC="https://studio.genlayer.com/api"
EX="https://explorer-studio.genlayer.com"
ROOT=Path(__file__).resolve().parents[1]
ZOD_BASE="0175a043c7dde9238c9984bce4e4c3471a65582c"
ZOD_HEAD="dc1a40a54a063c90dbaf08d841064d7aa0120ff8"
ZOD_VERSION="4.5.0-canary.20260817T002538"
GL_BASE="ae4805e09cf1626e2bfcc0b2e6e1b2639f8431cf"
GL_HEAD="a76bec395aaa927720ee0ce364899a64044dd43e"

def load_wallets():
    for raw in (ROOT.parent/"secrets"/"genlayer-test-wallets.env").read_text(encoding="utf-8").splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            k,v=raw.split("=",1); os.environ.setdefault(k.strip(),v.strip().strip("'\"").strip("<>"))

def plain(v):
    if isinstance(v,dict): return {str(k):plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [plain(x) for x in v]
    return v if isinstance(v,(str,int,float,bool)) or v is None else str(v)

def signals(info):
    status=str(info.get("status_name") or info.get("statusName") or info.get("status") or "UNKNOWN").upper()
    consensus=str(info.get("result_name") or info.get("consensus_result_name") or info.get("consensus_result") or "UNKNOWN").upper()
    data=info.get("consensus_data") if isinstance(info.get("consensus_data"),dict) else {}
    receipts=data.get("leader_receipt") or data.get("validators") or []
    if isinstance(receipts,dict): receipts=[receipts]
    leader=next((r for r in receipts if isinstance(r,dict) and str(r.get("mode","")).lower()=="leader"),receipts[0] if receipts else {})
    execution=str(leader.get("execution_result") or info.get("execution_result") or "UNKNOWN").upper()
    reason=leader.get("result",{}).get("payload","") if isinstance(leader.get("result"),dict) else ""
    return status,consensus,execution,reason

def read(client,address,account,method,args):
    last=None
    for i in range(10):
        try:return plain(client.read_contract(address=address,function_name=method,args=args,account=account))
        except Exception as e:last=e;time.sleep(2+i)
    raise last

def send(client,address,account,method,args,expect_success=True):
    tx=str(client.write_contract(address=address,function_name=method,account=account,args=args,value=0))
    print(json.dumps({"submitted":tx,"method":method}),flush=True)
    for _ in range(240):
        info=plain(client.get_transaction(tx)); status,consensus,execution,reason=signals(info)
        if status=="FINALIZED":
            success=consensus in {"MAJORITY_AGREE","AGREE","ACCEPTED"} and execution=="SUCCESS"
            if success!=expect_success: raise AssertionError((method,status,consensus,execution,reason,tx))
            return {"hash":tx,"url":f"{EX}/tx/{tx}","status":status,"consensus":consensus,"execution":execution,"reason":reason}
        time.sleep(3)
    raise TimeoutError(tx)

def register_and_inspect(client,address,wallet,args,expected):
    before=int(read(client,address,wallet,"get_config",[])["release_count"])
    register=send(client,address,wallet,"register_release",args)
    after=int(read(client,address,wallet,"get_config",[])["release_count"])
    if after!=before+1: raise AssertionError((before,after))
    registered=read(client,address,wallet,"get_release",[after])
    inspect=send(client,address,wallet,"inspect_release",[after])
    record=read(client,address,wallet,"get_release",[after])
    attempt=read(client,address,wallet,"get_inspection",[after,record["attempts"]])
    if record["state"]!=expected: raise AssertionError({"expected":expected,"record":record,"inspection":attempt})
    return after,{"register":register,"inspect":inspect,"registered":registered,"record":record,"inspection":attempt}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: run_studionet_e2e.py CONTRACT_ADDRESS")
    address=sys.argv[1];load_wallets()
    a=create_account(os.environ["SERVICE_LEDGER_KEY_A"]);b=create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    client=create_client(chain=studionet,account=a,endpoint=RPC)
    cfg=read(client,address,a,"get_config",[])
    if cfg.get("version")!="RELEASE_SEAL_V1":raise AssertionError(cfg)
    evidence={"network":"studionet","contract":address,"contract_url":f"{EX}/address/{address}","wallets":{"auxiliary_a":str(a.address),"auxiliary_b":str(b.address)},"initial_config":cfg,"cases":{}}
    happy=["colinhacks","zod",ZOD_BASE,ZOD_HEAD,"zod",ZOD_VERSION,"packages/zod/src/v4/locales","packages/zod/src/v4/core/tests"]
    rid,h=register_and_inspect(client,address,a,happy,"RELEASABLE")
    activate=send(client,address,b,"activate_release",[rid,h["record"]["artifact_integrity"]])
    h["activate"]=activate;h["activated"]=read(client,address,b,"get_release",[rid]);evidence["cases"]["happy_activation"]=h
    before=h["activated"]
    replay=send(client,address,a,"activate_release",[rid,h["record"]["artifact_integrity"]],False)
    after=read(client,address,a,"get_release",[rid])
    if before!=after:raise AssertionError("REPLAY_MUTATED_STATE")
    evidence["cases"]["activation_replay"]={"transaction":replay,"pre":before,"post":after}
    blocked=["genlayerlabs","genlayer-js",GL_BASE,GL_HEAD,"genlayer-js","1.1.8","src","tests"]
    _,neg=register_and_inspect(client,address,b,blocked,"BLOCKED");evidence["cases"]["no_production_change"]=neg
    conflict=["colinhacks","zod",ZOD_BASE,ZOD_HEAD,"zod","4.1.11","packages/zod/src/v4/locales","packages/zod/src/v4/core/tests"]
    _,con=register_and_inspect(client,address,b,conflict,"CONFLICT");evidence["cases"]["package_commit_conflict"]=con
    final=read(client,address,a,"get_config",[]);evidence["final_config"]=final
    (ROOT/"docs"/"studionet-e2e.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(evidence,indent=2))

if __name__=="__main__":main()
