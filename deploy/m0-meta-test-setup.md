# M0 setup: Meta WhatsApp test environment

Purpose: prove the connectivity path WhatsApp → signed webhook → Django → queue → worker → fixed test response → WhatsApp. M0 is not a chatbot and must not be used with customers.

## Rules for M0

- Use only Meta's test phone number and test recipient numbers that you own or that Meta provides for testing.
- No real customer numbers, names, or messages. No LLM. No lead qualification.
- No templates. Replies are session messages sent inside the 24-hour service window, so the tester must write first.
- Secrets are supplied only through environment variables (see `.env.example`). Do not paste them into files, tickets, or chat.

## Steps (owner)

1. In the Meta developer dashboard, create an app and add the WhatsApp product. Use the test phone number that Meta provides.
2. Record the values in your local `.env` (never committed): `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN` (a value you choose), `WHATSAPP_ACCESS_TOKEN` (temporary test token), `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_GRAPH_API_VERSION` (check the current version in Meta's documentation).
3. Compute the HMAC of your test recipient number with `SALESAGENT_LOG_HMAC_KEY` and put it in `WHATSAPP_TEST_RECIPIENT_HMACS`. The number itself is never stored in the configuration.
4. Expose the local web service over HTTPS for the test only, using a temporary tunnel or a staging host. Set the Meta callback URL to `https://<test-host>/webhooks/whatsapp/`.
5. Subscribe the app to the `messages` webhook field, and confirm the verification request succeeds.
6. Set `WHATSAPP_M0_MODE=true`, start the stack (`docker compose -f deploy/docker-compose.yml up --build`), and run the worker with `process_inbox`.
7. From the allowlisted test phone, send any text. Expect the fixed response within the service window.
8. After the run, delete the temporary tunnel and rotate the temporary access token. Run `python manage.py m0_purge_test_data`.

## Production warning

`WHATSAPP_M0_MODE=true` must never be set in production. The production settings module refuses to start with it enabled (see `src/salesagent/settings/production.py`, and the readiness gate T141).
