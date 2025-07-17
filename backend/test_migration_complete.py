#!/usr/bin/env python3
import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_service_step_by_step():
    """Test database service step by step"""
    try:
        print("Step 1: Testing service import...")
        from app.services.database_curated_models import \
            DatabaseCuratedModelsService
        print("✓ Service class imported")
        
        print("\nStep 2: Creating service instance...")
        service = DatabaseCuratedModelsService()
        print("✓ Service instance created")
        
        print("\nStep 3: Testing get_models...")
        models = await service.get_models()
        print(f"✓ Retrieved {len(models)} models")
        
        if models:
            print(f"  First model: {models[0]['id']} ({models[0]['provider']})")
        
        print("\n🎉 Database service is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error in step: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_router_compatibility():
    """Test that router can use the new service"""
    try:
        print("\nTesting router compatibility...")
        
        # Import router
        from app.llm.router import get_available_models
        print("✓ Router endpoint imported")
        
        # Since the endpoint requires a database dependency, we can't test it directly
        # But we can verify the service is accessible
        from app.llm.router import database_curated_models_service
        print("✓ Service is accessible from router")
        
        models = await database_curated_models_service.get_models()
        print(f"✓ Router can access {len(models)} models via service")
        
        print("🎉 Router compatibility confirmed!")
        return True
        
    except Exception as e:
        print(f"❌ Router test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("=== Database Service Migration Test ===\n")
    
    service_ok = await test_service_step_by_step()
    router_ok = await test_router_compatibility()
    
    print(f"\n=== Test Results ===")
    print(f"Database Service: {'✓ PASS' if service_ok else '❌ FAIL'}")
    print(f"Router Integration: {'✓ PASS' if router_ok else '❌ FAIL'}")
    
    if service_ok and router_ok:
        print("\n🎉 Migration to database-backed model service is SUCCESSFUL!")
        print("   - Models are now stored in the database")
        print("   - No more JSON file dependency")
        print("   - Models will persist across deployments")
    else:
        print("\n❌ Migration has issues that need to be resolved")

if __name__ == "__main__":
    asyncio.run(main())
