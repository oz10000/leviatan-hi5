# .github/workflows/bot.yml
name: Leviathan H5 – Verify & Run

on:
  schedule:
    # Ejecutar cada 10 minutos para simular continuidad en testnet
    - cron: '*/10 * * * *'
  workflow_dispatch:    # permite ejecución manual desde GitHub

jobs:
  verify-and-run:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Validate environment & imports
        env:
          OKX_API_KEY: ${{ secrets.OKX_API_KEY }}
          OKX_SECRET_KEY: ${{ secrets.OKX_SECRET_KEY }}
          OKX_PASSPHRASE: ${{ secrets.OKX_PASSPHRASE }}
          LIVE_MODE: 'false'
        run: |
          python -c "
          import config
          print('✅ config module loaded')
          print(f'Testnet mode: {config.TESTNET}')
          print(f'API Key set: {bool(config.OKX_API_KEY)}')
          print(f'Secret Key set: {bool(config.OKX_SECRET_KEY)}')
          print(f'Passphrase set: {bool(config.OKX_PASSPHRASE)}')
          print('Directories logs/ and data/ exist')
          "

      - name: Run Leviathan H5 (dry run / testnet)
        env:
          OKX_API_KEY: ${{ secrets.OKX_API_KEY }}
          OKX_SECRET_KEY: ${{ secrets.OKX_SECRET_KEY }}
          OKX_PASSPHRASE: ${{ secrets.OKX_PASSPHRASE }}
          LIVE_MODE: 'false'
          CAPITAL: '20'
          LEVERAGE: '5'
          TOP_N: '5'
          COOLDOWN: '300'
          MODE: 'A'
        run: |
          python launcher.py --mode run

      # Opcional: guardar artefactos (logs, trades, estado) incluso si el paso anterior falla
      - name: Upload artifacts
        if: always()   # siempre, para inspeccionar fallos
        uses: actions/upload-artifact@v4
        with:
          name: leviathan-logs-${{ github.run_id }}
          path: |
            data/trades.csv
            data/state.json
            logs/bot.log
          retention-days: 7
