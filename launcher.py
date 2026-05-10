#!/usr/bin/env python3
"""
LEVIATHAN HIGHFIVE V5 — Launcher
Handles CLI arguments and dispatches to the correct execution mode.
"""
import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser(description="Leviathan HighFive V5")
    parser.add_argument("--mode", choices=["run", "backtest", "mc", "wf"],
                        default="run", help="Execution mode")
    parser.add_argument("--console", action="store_true", default=True,
                        help="ASCII console output (default)")
    parser.add_argument("--dashboard", action="store_true",
                        help="Start Streamlit dashboard (blocks)")

    args = parser.parse_args()

    if args.dashboard:
        print("[LEVIATHAN] Starting Streamlit dashboard...")
        os.system("streamlit run dashboard/app.py")
        return

    if args.mode == "run":
        from main import LeviathanBot
        bot = LeviathanBot(use_live=False)  # paper first; LIVE_MODE in .env
        bot.run()

    elif args.mode == "backtest":
        from analytics.walkforward import run_walkforward
        print("[LEVIATHAN] Running walk-forward backtest...")
        results = run_walkforward()
        print(results)

    elif args.mode == "mc":
        from analytics.monte_carlo import run_monte_carlo
        print("[LEVIATHAN] Running Monte Carlo simulation...")
        results = run_monte_carlo(num_runs=2000)
        print(results)

    elif args.mode == "wf":
        from analytics.walkforward import run_walkforward
        print("[LEVIATHAN] Running walk-forward validation...")
        wf = run_walkforward()
        print(wf)


if __name__ == "__main__":
    main()
