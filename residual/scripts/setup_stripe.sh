#!/usr/bin/env bash
# Requires STRIPE_SECRET_KEY in env. Creates products + payment links.
set -euo pipefail
: "${STRIPE_SECRET_KEY:?set STRIPE_SECRET_KEY}"
API="https://api.stripe.com/v1"
AUTH=(-u "${STRIPE_SECRET_KEY}:")
JSON=(-H "Content-Type: application/x-www-form-urlencoded")

create_product() {
  local name="$1" tier="$2" amount="$3"
  local prod
  prod=$(curl -sS "${AUTH[@]}" "${JSON[@]}" -X POST "${API}/products" \
    -d "name=${name}" -d "metadata[tier]=${tier}")
  local pid
  pid=$(echo "$prod" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
  local price
  price=$(curl -sS "${AUTH[@]}" "${JSON[@]}" -X POST "${API}/prices" \
    -d "product=${pid}" -d "unit_amount=${amount}" \
    -d "currency=usd" -d "recurring[interval]=year")
  local prid
  prid=$(echo "$price" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
  echo "product=${pid} price=${prid}"
  echo "${pid}" > ".stripe_${tier}_product"
  echo "${prid}" > ".stripe_${tier}_price"
}

echo "→ creating solo product"
create_product "residual solo" "solo" 9900
echo "→ creating team product"
create_product "residual team" "team" 99900

echo "→ creating payment links"
for tier in solo team; do
  prid=$(cat ".stripe_${tier}_price")
  link=$(curl -sS "${AUTH[@]}" "${JSON[@]}" -X POST "${API}/payment_links" \
    -d "line_items[0][price]=${prid}" \
    -d "line_items[0][quantity]=1" \
    -d "metadata[tier]=${tier}")
  url=$(echo "$link" | python3 -c 'import sys,json;print(json.load(sys.stdin)["url"])')
  echo "  ${tier}: ${url}"
  echo "${url}" > ".stripe_${tier}_link"
done

echo
echo "Payment links:"
cat .stripe_*_link 2>/dev/null
echo
echo "Next: Stripe Dashboard → Developers → Webhooks → Add endpoint"
echo "  URL: https://residual-webhook.fly.dev/stripe"
echo "  Events: checkout.session.completed"
