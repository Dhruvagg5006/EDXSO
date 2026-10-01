"""
Command Line Interface (CLI) for Automated Micro-Influencer Outreach System.
Allows running individual pipeline stages or complete end-to-end execution.
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.pipeline import MicroInfluencerPipeline
from src.sending.tracker import OutreachTracker

def main():
    parser = argparse.ArgumentParser(
        description="Automated Micro-Influencer Outreach System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--run-all", action="store_true", help="Execute complete end-to-end outreach pipeline")
    parser.add_argument("--niche", type=str, default=config.TARGET_NICHE, help=f"Target niche (default: {config.TARGET_NICHE})")
    parser.add_argument("--live", action="store_true", help="Enable live SMTP delivery (default: DRY_RUN simulation)")
    parser.add_argument("--reset-tracker", action="store_true", help="Reset outreach tracker database for fresh run")
    parser.add_argument("--show-logs", action="store_true", help="Display recent outreach logs from SQLite database")

    args = parser.parse_args()

    if args.reset_tracker:
        tracker = OutreachTracker()
        tracker.clear_tracker()
        print("Outreach tracker database reset successfully.")
        return

    if args.show_logs:
        tracker = OutreachTracker()
        logs = tracker.get_all_logs()
        print(f"\n--- Outreach Tracker Audit Log ({len(logs)} entries) ---")
        for log in logs[:15]:
            print(f"[{log['sent_at']}] {log['influencer_name']} | {log['channel']} | Status: {log['status']} | Email: {log['email']}")
        if len(logs) > 15:
            print(f"... and {len(logs) - 15} more entries in {config.DB_PATH}")
        return

    dry_run = not args.live
    print(f"Initializing pipeline: Niche='{args.niche}', DryRun={dry_run}")
    pipeline = MicroInfluencerPipeline(niche=args.niche, dry_run=dry_run)
    summary = pipeline.run_full_pipeline()

    print("\n" + "=" * 50)
    print("      PIPELINE EXECUTION COMPLETE")
    print("=" * 50)
    for k, v in summary.items():
        print(f"  {k:20}: {v}")
    print("=" * 50)

if __name__ == "__main__":
    main()
