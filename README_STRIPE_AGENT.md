# Stripe Agent Integration (Quickstart)

1. Paste your Stripe secret in `.env`:
   ```env
   STRIPE_SECRET_KEY=sk_test_...mcIw
   USD_PER_MESH=5
   CHECKOUT_REDIRECT_BASE=https://yourdomain.com/pay/
   # Add STRIPE_ENDPOINT_SECRET if using webhooks
   ```

2. Install dependencies:
   ```bash
   pip install stripe-agent-toolkit
   ```

3. Run the sample agent:
   ```bash
   python stripe_agent_example.py
   ```

4. Result: Stripe payment link for a $100 product called "Test" is printed.

---

If you need to customize, add more actions, or debug, ask your agent (me) for help!