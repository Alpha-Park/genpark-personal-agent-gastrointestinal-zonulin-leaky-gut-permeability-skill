# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-gastrointestinal-zonulin-leaky-gut-permeability-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def evaluate_gut_barrier_permeability(serum_zonulin_ng_ml, lps_endotoxin_eu_ml=0.35, calprotectin_ug_g=30.0):
    if serum_zonulin_ng_ml <= 0:
        raise ValueError("serum_zonulin_ng_ml must be positive")
        
    # Zonulin reference ranges:
    # < 38.0 ng/mL: Intact epithelial tight junctions (Claudin/Occludin intact)
    # 38.0 - 55.0 ng/mL: Mild to moderate mucosal hyperpermeability
    # > 55.0 ng/mL: Severe tight junction disassembly (Leaky Gut Syndrome)
    if serum_zonulin_ng_ml < 38.0:
        permeability_status = "INTACT_EPITHELIAL_BARRIER"
        translocation_risk = "LOW"
    elif serum_zonulin_ng_ml <= 55.0:
        permeability_status = "ELEVATED_INTESTINAL_PERMEABILITY"
        translocation_risk = "MODERATE"
    else:
        permeability_status = "SEVERE_MUCOSAL_BARRIER_DISASSEMBLY"
        translocation_risk = "HIGH_SYSTEMIC_ENDOTOXEMIA"
        
    # LPS bacterial translocation assessment (normal < 0.5 EU/mL)
    endotoxemia_present = lps_endotoxin_eu_ml > 0.5
    mucosal_inflammation = calprotectin_ug_g > 50.0
    
    # Combined Barrier Breakdown Index (0 - 100)
    score = min(100.0, (serum_zonulin_ng_ml / 60.0) * 50.0 + (lps_endotoxin_eu_ml / 1.0) * 30.0 + (calprotectin_ug_g / 100.0) * 20.0)
    
    return {
        "serum_zonulin_ng_ml": round(serum_zonulin_ng_ml, 2),
        "lps_endotoxin_eu_ml": round(lps_endotoxin_eu_ml, 3),
        "fecal_calprotectin_ug_g": round(calprotectin_ug_g, 1),
        "intestinal_barrier_status": permeability_status,
        "gut_permeability_score_0_to_100": round(score, 1),
        "bacterial_endotoxin_translocation": endotoxemia_present,
        "mucosal_neutrophil_inflammation": mucosal_inflammation,
        "dietary_guidance": "Eliminate dietary gluten, emulsifiers, NSAIDs; consider zinc carnosine, L-glutamine, and spore probiotics." if score > 50.0 else "Healthy intestinal tight-junction homeostasis."
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "evaluate_gut_barrier_permeability",
                        "description": """Evaluate intestinal mucosal barrier integrity and tight-junction disassembly using serum Zonulin (ng/mL) and lipopolysaccharide (LPS, EU/mL).
Computes leaky gut mucosal breakdown index, systemic endotoxemia hazard, and systemic inflammatory trigger score.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = evaluate_gut_barrier_permeability(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'serum_zonulin_ng_ml': 46.5, 'lps_endotoxin_eu_ml': 0.62, 'calprotectin_ug_g': 65.0}
        out = evaluate_gut_barrier_permeability(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
