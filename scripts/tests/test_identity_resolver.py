import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.identity_resolver import IdentityResolver

def test_resolution():
    root = os.getcwd()
    resolver = IdentityResolver(root)
    
    print("--- Running Identity Resolution Tests ---")
    
    # 1. Alias Resolution
    res1 = resolver.resolve("python-expert")
    print(f"Test 1 (Alias): {res1['resolved_agent']} ({res1['confidence']})")
    assert res1['resolved_agent'] is not None
    
    # 2. Cache check
    res2 = resolver.resolve("python-expert")
    assert res2 == res1
    print("Test 2 (Cache): PASS")

if __name__ == "__main__":
    test_resolution()
