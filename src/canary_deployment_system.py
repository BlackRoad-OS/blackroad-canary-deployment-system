#!/usr/bin/env python3
"""BlackRoad Canary Deployment — traffic splitting + automatic rollback."""
import json, time, random, os

class CanaryRouter:
    def __init__(self, stable_url: str, canary_url: str, canary_pct: float = 0.05):
        self.stable = stable_url
        self.canary = canary_url
        self.canary_pct = canary_pct
        self.metrics = {"stable": {"ok": 0, "err": 0}, "canary": {"ok": 0, "err": 0}}

    def route(self) -> tuple[str, str]:
        if random.random() < self.canary_pct:
            return self.canary, "canary"
        return self.stable, "stable"

    def record(self, variant: str, success: bool):
        key = "ok" if success else "err"
        self.metrics[variant][key] += 1

    def error_rate(self, variant: str) -> float:
        m = self.metrics[variant]
        total = m["ok"] + m["err"]
        return m["err"] / total if total > 0 else 0.0

    def should_rollback(self, threshold: float = 0.05) -> bool:
        canary_rate = self.error_rate("canary")
        stable_rate = self.error_rate("stable")
        if canary_rate > threshold and canary_rate > stable_rate * 2:
            return True
        return False

    def report(self):
        print("\\n🐤 Canary Deployment Report")
        for variant in ["stable", "canary"]:
            m = self.metrics[variant]
            total = m["ok"] + m["err"]
            err_rate = self.error_rate(variant) * 100
            print(f"  {variant:<8}: {m[\"ok\"]} ok / {m[\"err\"]} err / {total} total — {err_rate:.1f}% error")
        if self.should_rollback():
            print("  ⚠️  ROLLBACK RECOMMENDED — canary error rate too high")
        else:
            print("  ✅ Canary healthy — consider increasing traffic split")

if __name__ == "__main__":
    router = CanaryRouter("https://api.blackroad.io", "https://canary.api.blackroad.io", 0.1)
    for i in range(100):
        url, variant = router.route()
        success = random.random() > (0.02 if variant == "stable" else 0.08)
        router.record(variant, success)
    router.report()

