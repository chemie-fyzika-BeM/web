#!/bin/zsh
cd -- "${0:A:h}"
for runtime in /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if [[ -x "$runtime" ]]; then
    exec "$runtime" server.py
  fi
done
if command -v python3 >/dev/null 2>&1; then
  exec python3 server.py
fi
echo 'Pro spuštění je potřeba Python 3 z python.org. Potom znovu otevřete tento soubor.'
read '?Stiskněte Enter pro zavření.'
