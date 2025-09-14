#!/usr/bin/env bash
TARGET="1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"

while IFS= read -r phrase; do
  echo -e "\n=== Testing ===\n$phrase\n"
  # Derive index-0 address only
  addr=$(python derive_keys.py "$phrase" 2>/dev/null | awk '/^[[:space:]]*0:/ { print $2 }')
  echo "Index 0 → $addr"

  if [[ "$addr" == "$TARGET" ]]; then
    echo -e "\n🎉 🏆 MATCH FOUND FOR:\n$phrase"
    exit 0
  fi
done < candidates.txt

echo -e "\nNo candidate produced the target at index 0."
exit 1
