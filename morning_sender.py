name: Eitaa Morning Message

on:
  schedule:
    - cron: "30 2 * * *"
  workflow_dispatch:

jobs:
  send-morning:
    runs-on: ubuntu-latest

    steps:
      - name: Download files
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install requests
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Send Eitaa messages
        env:
          EITAA_TOKEN: ${{ secrets.EITAA_TOKEN }}
        run: python morning_sender.py
