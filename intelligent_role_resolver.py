# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
from dataclasses import dataclass


def _url_ok(url: str) -> bool:
    return url.startswith("https://") or url.startswith("http://")

def _clean(value: str, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]

def _score(value) -> int:
    try:
        n = int(value)
    except Exception:
        return 0
    if n < 0:
        return 0
    if n > 100:
        return 100
    return n

def _parse(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}

def _fingerprint(text: str) -> str:
    # Deterministic, compact content marker; not a cryptographic hash.
    total = 2166136261
    for ch in text[:30000]:
        total = (total ^ ord(ch)) * 16777619
        total = total % 4294967296
    return str(total) + ":" + str(len(text))

def _page(url: str) -> str:
    try:
        response = gl.nondet.web.get(url)
        body = response.body.decode("utf-8")
        if not body:
            return "__WEB_ERROR__:empty"
        return body[:30000]
    except Exception:
        return "__WEB_ERROR__:fetch_failed"

@allow_storage
@dataclass
class RoleCase:
    subject: str
    evidence_url: str
    role: str
    criteria: str
    status: str
    score: u8
    reason: str
    source_fingerprint: str
    version: u32


class IntelligentRoleResolver(gl.Contract):
    cases: TreeMap[str, RoleCase]

    def __init__(self):
        pass

    @gl.public.write
    def create_case(self, case_id: str, subject: str, evidence_url: str, role: str, criteria: str) -> None:
        if not case_id or case_id in self.cases: raise gl.vm.UserError("Invalid or duplicate case id")
        if not _url_ok(evidence_url): raise gl.vm.UserError("Evidence URL must be HTTP or HTTPS")
        if not subject.strip() or not role.strip() or not criteria.strip(): raise gl.vm.UserError("Subject, role and criteria are required")
        self.cases[case_id] = RoleCase(subject[:200], evidence_url[:500], role[:160], criteria[:2500], "PENDING", u8(0), "", "", u32(0))

    @gl.public.write
    def resolve(self, case_id: str) -> str:
        item = self.cases.get(case_id)
        if item is None:
            raise gl.vm.UserError("Case not found")
        if item.status not in ("PENDING", "UNVERIFIABLE", "UNCERTAIN", "INSUFFICIENT_EVIDENCE"):
            raise gl.vm.UserError("Case is already finalized")
        sources = [("EVIDENCE", item.evidence_url, 20000)]
        def source() -> str:
            parts = []
            for label, url, limit in sources:
                body = _page(url)
                parts.append(label + "_FINGERPRINT=" + _fingerprint(body) + "\n" + label + "_CONTENT=\n" + body[:limit])
            return "\n\n".join(parts)
        raw = gl.eq_principle.prompt_non_comparative(
            source,
            task='Determine eligibility for a role using only the supplied public evidence. Return ONLY JSON: {"status":"ELIGIBLE|NOT_ELIGIBLE|INSUFFICIENT_EVIDENCE","score":0,"reason":"short factual reason","source_fingerprint":"marker"}. Do not infer private or sensitive facts.',
            criteria='ELIGIBLE requires affirmative evidence for the stated criteria. NOT_ELIGIBLE requires evidence failing a material criterion. Otherwise INSUFFICIENT_EVIDENCE. Do not infer facts that are not public in the source.',
        )
        data = _parse(raw)
        status = str(data.get("status", "INSUFFICIENT_EVIDENCE"))
        if status not in ('ELIGIBLE', 'NOT_ELIGIBLE', 'INSUFFICIENT_EVIDENCE'):
            status = "INSUFFICIENT_EVIDENCE"
        score = _score(data.get("score", 0))
        reason = _clean(str(data.get("reason", "Insufficient evidence.")), 1200)
        fp = _clean(str(data.get("source_fingerprint", "")), 120)
        self.cases[case_id] = RoleCase(item.subject, item.evidence_url, item.role, item.criteria, status, u8(score), reason, fp, item.version + u32(1))
        return json.dumps({"status": status, "score": score, "version": str(item.version + u32(1))})

    @gl.public.view
    def get_case(self, case_id: str) -> str:
        item = self.cases.get(case_id)
        if item is None:
            return ""
        return json.dumps({'subject': item.subject, 'evidence_url': item.evidence_url, 'role': item.role, 'criteria': item.criteria, 'status': item.status, 'score': item.score, 'reason': item.reason, 'source_fingerprint': item.source_fingerprint, 'version': item.version}, sort_keys=True)
