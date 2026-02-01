#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from analyzer import Analyzer


def main():
    """Analyze results and create data files"""
    print("=== LLM Reflective Questioning Benchmark ===")
    print("Phase 4: Analysis")
    print("-" * 40)

    analyzer = Analyzer()

    # Load data
    try:
        analyzer.load_data()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please run the previous scripts first to generate data.")
        return

    # NOTE: Visualizations are rendered interactively in HTML using Chart.js
    # No static PNG files are generated
    print("📊 Analysis phase: Data processing complete")
    print("   (Charts will be rendered interactively in HTML)")

    # Save results
    print("💾 Saving results...")
    analyzer.save_results()

    # Copy summary.json to web/data/ for interactive HTML charts
    import shutil
    web_summary_path = Path(__file__).parent.parent / "docs" / "data" / "summary.json"
    web_summary_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy("results/summary.json", web_summary_path)
    print(f"📁 Copied summary.json to web/data/ for interactive HTML")

    # Copy evaluations.json to web/data/ for interactive evaluations
    web_eval_path = Path(__file__).parent.parent / "docs" / "data" / "evaluations.json"
    shutil.copy("data/evaluations.json", web_eval_path)
    print(f"📁 Copied evaluations.json to web/data/ for interactive HTML")

    print("\n✅ Analysis complete!")
    print("📁 Files generated:")
    print("   - results/summary.md (Human-readable findings)")
    print("   - results/summary.json (Machine-readable data)")
    print("   - web/data/summary.json (For interactive HTML charts)")
    print("   - web/data/evaluations.json (For interactive HTML evaluations)")

    print("\n🎯 Open results/summary.md to view findings!")


if __name__ == "__main__":
    main()