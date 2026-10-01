import json
from pathlib import Path
import pytest

CONTRACT = Path(__file__).parents[1] / "contracts" / "release_seal.py"
ALICE = bytes.fromhex("11" * 20)
BOB = bytes.fromhex("22" * 20)
BASE = "a" * 40
HEAD = "b" * 40


def deploy(vm, direct_deploy):
    vm.strict_mocks = True
    vm.check_pickling = True
    with vm.prank(ALICE): return direct_deploy(CONTRACT, sdk_version="v0.2.16")


def sources(vm, *, prod=True, tests=True, check_head=HEAD, conclusion="success",
            package_head=HEAD, integrity="sha512-verified", semantic="YES", status=200):
    paths = []
    if prod: paths.append({"filename":"src/core.js","patch":"+export const release = true"})
    if tests: paths.append({"filename":"tests/core.test.js","patch":"+assert.equal(release, true)"})
    compare = {"status":"ahead", "base_commit":{"sha":BASE}, "merge_base_commit":{"sha":BASE},
               "commits":[{"sha":HEAD}], "files":paths}
    checks = {"check_runs":[{"name":"test", "head_sha":check_head, "status":"completed", "conclusion":conclusion}]}
    package = {"name":"release-demo", "version":"1.0.0", "gitHead":package_head,
               "dist":{"integrity":integrity, "tarball":"https://registry.npmjs.org/release-demo/-/release-demo-1.0.0.tgz"}}
    vm.mock_web(r"api\.github\.com/repos/acme/release-demo/commits/"+HEAD+r"$", {"method":"GET","status":status,"body":json.dumps({"sha":HEAD})})
    if status != 200:
        return
    vm.mock_web(r"api\.github\.com/repos/acme/release-demo/compare/"+BASE+r"\.\.\."+HEAD+r"\?per_page=100", {"method":"GET","status":status,"body":json.dumps(compare)})
    vm.mock_web(r"api\.github\.com/repos/acme/release-demo/commits/"+HEAD+r"/check-runs\?per_page=100", {"method":"GET","status":status,"body":json.dumps(checks)})
    vm.mock_web(r"registry\.npmjs\.org/release-demo/1\.0\.0", {"method":"GET","status":status,"body":json.dumps(package)})
    if status == 200:
        vm.mock_llm("RELEASE_SEAL_ALIGNMENT_V1", {"test_alignment":semantic,"risk_tier":"MEDIUM"})


def register(c, vm, sender=ALICE):
    with vm.prank(sender):
        return c.register_release("acme","release-demo",BASE,HEAD,"release-demo","1.0.0","src","tests")


def inspect(c, vm, rid=1, sender=BOB):
    with vm.prank(sender): c.inspect_release(rid)


def test_happy_release_and_permissionless_activation(direct_vm, direct_deploy):
    c=deploy(direct_vm,direct_deploy); sources(direct_vm); assert register(c,direct_vm)==1; inspect(c,direct_vm)
    r=c.get_release(1); assert r["state"]=="RELEASABLE" and r["reason"]=="SOURCE_CI_ARTIFACT_ALIGNED"
    assert r["artifact_integrity"]=="sha512-verified" and len(r["evidence_digest"])==64
    with direct_vm.prank(bytes.fromhex("33"*20)): c.activate_release(1,"sha512-verified")
    r=c.get_release(1); assert r["state"]=="ACTIVATED" and len(r["activation_digest"])==64


@pytest.mark.parametrize("change,expected", [
    ({"prod":False},("BLOCKED","NO_PRODUCTION_CHANGE")),
    ({"tests":False},("BLOCKED","NO_REGRESSION_CHANGE")),
    ({"conclusion":"failure"},("BLOCKED","REQUIRED_CHECKS_NOT_PASSING")),
    ({"check_head":"c"*40},("CONFLICT","CHECKS_NOT_BOUND_TO_HEAD")),
    ({"package_head":"c"*40},("CONFLICT","PACKAGE_COMMIT_MISMATCH")),
    ({"integrity":""},("BLOCKED","ARTIFACT_INTEGRITY_MISSING")),
    ({"semantic":"NO"},("BLOCKED","REGRESSION_ALIGNMENT_NOT_PROVEN")),
    ({"semantic":"UNKNOWN"},("UNRESOLVED","REGRESSION_ALIGNMENT_NOT_PROVEN")),
])
def test_fail_closed_matrix(direct_vm,direct_deploy,change,expected):
    c=deploy(direct_vm,direct_deploy); sources(direct_vm,**change); register(c,direct_vm); inspect(c,direct_vm)
    r=c.get_release(1); assert (r["state"],r["reason"])==expected


def test_source_unavailable_retry_remains_fail_closed(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); sources(direct_vm,status=503); register(c,direct_vm); inspect(c,direct_vm)
    assert c.get_release(1)["state"]=="UNRESOLVED"
    inspect(c,direct_vm)
    record=c.get_release(1); assert record["state"]=="UNRESOLVED" and record["attempts"]==2


def test_wrong_integrity_rolls_back_complete_state(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); sources(direct_vm); register(c,direct_vm); inspect(c,direct_vm)
    before=c.get_release(1); cfg=c.get_config()
    with direct_vm.prank(BOB), direct_vm.expect_revert("ARTIFACT_INTEGRITY_MISMATCH"):
        c.activate_release(1,"sha512-attacker")
    assert c.get_release(1)==before and c.get_config()==cfg


def test_activation_replay_rejected(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); sources(direct_vm); register(c,direct_vm); inspect(c,direct_vm)
    with direct_vm.prank(BOB): c.activate_release(1,"sha512-verified")
    before=c.get_release(1)
    with direct_vm.prank(ALICE), direct_vm.expect_revert("RELEASE_NOT_RELEASABLE"):
        c.activate_release(1,"sha512-verified")
    assert c.get_release(1)==before


def test_registration_replay_and_invalid_input_rollback(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); register(c,direct_vm); before=c.get_config()
    with direct_vm.prank(BOB), direct_vm.expect_revert("RELEASE_ALREADY_REGISTERED"): register(c,direct_vm,BOB)
    assert c.get_config()==before
    with direct_vm.prank(BOB), direct_vm.expect_revert("INVALID_HEAD_COMMIT"):
        c.register_release("acme","release-demo",BASE,"bad","release-demo","1.0.0","src","tests")
    assert c.get_config()==before


def test_any_wallet_can_register_and_inspect(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); sources(direct_vm); rid=register(c,direct_vm,BOB); inspect(c,direct_vm,rid,ALICE)
    assert c.get_release(rid)["creator"]=="0x"+"22"*20


def test_config_and_runner(direct_vm,direct_deploy):
    c=deploy(direct_vm,direct_deploy); cfg=c.get_config()
    assert cfg["version"]=="RELEASE_SEAL_V1" and cfg["architecture"]=="REVISION_BOUND_MULTI_SOURCE_ACTIVATION_GATE"
    assert CONTRACT.read_text(encoding="utf-8").splitlines()[:2]==["# v0.2.16",'# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }']
