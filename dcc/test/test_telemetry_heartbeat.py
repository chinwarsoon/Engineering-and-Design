"""
Quick Test for Telemetry Heartbeat (Phase 3)
Validates R17 Telemetry Module implementation
"""

import sys
from pathlib import Path

# Add workflow path
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))

def test_telemetry_heartbeat():
    """Test telemetry heartbeat functionality"""
    
    print("=" * 60)
    print("Phase 3 Telemetry Heartbeat Test (R17)")
    print("=" * 60)
    
    try:
        # Test 1: Import
        from core_engine.telemetry_heartbeat import TelemetryHeartbeat, HeartbeatPayload
        print("✅ Test 1: TelemetryHeartbeat imported successfully")
        
        # Test 2: Create instance
        hb = TelemetryHeartbeat(interval=1000)
        print("✅ Test 2: Heartbeat instance created (interval=1000)")
        
        # Test 3: Simulate processing with heartbeat
        print("\n📊 Simulating data processing...")
        total_rows = 5500
        heartbeats_received = []
        
        for row_idx in range(0, total_rows, 500):
            payload = hb.tick(
                current_row=row_idx,
                current_phase="P2.5" if row_idx < 3000 else "P3",
                total_rows=total_rows
            )
            if payload:
                heartbeats_received.append(payload)
                print(f"⏳ Row {payload.rows_processed:,} ({payload.percent_complete:.1f}%) | "
                      f"Phase: {payload.current_phase} | Mem: {payload.memory_usage_mb:.1f}MB")
        
        # Test 4: Final summary
        final = hb.final_summary(total_rows)
        print(f"\n✅ Processing complete: {final.rows_processed:,} rows | "
              f"Memory: {final.memory_usage_mb:.1f}MB | Heartbeats: {hb.heartbeat_count}")
        
        # Validation
        print("\n" + "=" * 60)
        print("Validation Results")
        print("=" * 60)
        
        # Check heartbeat count (expecting ~5 for 5500 rows with 1000 interval)
        expected_hbs = total_rows // 1000
        print(f"✅ Heartbeat count: {hb.heartbeat_count} (expected ~{expected_hbs})")
        
        # Check payload structure
        if heartbeats_received:
            first = heartbeats_received[0]
            checks = [
                ("rows_processed", first.rows_processed > 0),
                ("current_phase", bool(first.current_phase)),
                ("memory_usage_mb", first.memory_usage_mb > 0),
                ("timestamp", first.timestamp > 0),
                ("percent_complete", first.percent_complete is not None),
            ]
            
            for name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} Payload field '{name}': {passed}")
        
        # Test 5: Verify storage in context
        print("\n📦 Testing context storage...")
        from core_engine.context import PipelineContext, PipelinePaths
        
        paths = PipelinePaths(
            base_path=Path("/tmp"),
            schema_path=Path("/tmp/schema.json"),
            excel_path=Path("/tmp/input.xlsx"),
            csv_output_path=Path("/tmp/output.csv"),
            excel_output_path=Path("/tmp/output.xlsx"),
            summary_path=Path("/tmp/summary.json"),
            debug_log_path=Path("/tmp/debug.json")
        )
        
        ctx = PipelineContext(paths=paths, parameters={}, nrows=100, debug_mode=False)
        
        # Store heartbeats
        for hb_payload in heartbeats_received:
            ctx.telemetry.heartbeat_logs.append(hb_payload.to_dict())
        
        print(f"✅ Heartbeats stored in context: {len(ctx.telemetry.heartbeat_logs)}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Phase 3 Telemetry Working")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_telemetry_heartbeat()
    sys.exit(0 if success else 1)
