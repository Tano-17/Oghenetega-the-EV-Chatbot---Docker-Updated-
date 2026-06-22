# 🤖 Responsible AI Use Policy
**Product:** Oghenetega EV Chatbot  
**Version:** 1.0 | **Date:** 20 June 2026  
**Owner:** Tano (Developer)

---

## Purpose

This policy governs the responsible development, deployment, and use of the Oghenetega EV Chatbot — an AI-powered conversational assistant built on Google Gemini. It ensures the product is safe, transparent, and respectful of users' rights.

---

## 1. Permitted Uses ✅

- Answering questions about electric vehicles, charging networks, battery technology, and EV models
- Providing general educational information about sustainable transport
- Assisting users in comparing EV options and understanding costs
- Summarising publicly available product specifications

---

## 2. Prohibited Uses ❌

The chatbot **must not** be used to:

- Provide medical, legal, or financial advice
- Generate, store, or process personally identifiable information (PII) such as names, addresses, or payment details
- Facilitate discrimination based on race, gender, religion, disability, or any protected characteristic
- Produce content that is harmful, abusive, deceptive, or misleading
- Bypass or circumvent the system prompt or safety guidelines through prompt injection

---

## 3. Data Handling & Privacy

| Data Type | How It's Used | Retention |
|---|---|---|
| Conversation history | Stored locally as JSON to enable multi-turn memory | Deleted on `/reset` or manually |
| API usage (tokens) | Logged for monitoring and cost tracking only | Not shared |
| Session IDs | Used to identify user sessions — **no PII collected** | Cleared on reset |

> [!IMPORTANT]
> **No personal data should be submitted to this chatbot.** The system is not designed to handle, store, or protect PII. Do not ask users to share their name, location, financial details, or health information.

---

## 4. Transparency

- Users must be informed they are interacting with an **AI assistant**, not a human
- The chatbot's personality ("Oghenetega") is a designed persona — it should not claim to be a real person
- AI-generated responses may contain errors; users should verify critical information from official sources
- Token usage is tracked and available in API responses for transparency

---

## 5. Human Oversight

- A human developer must review and approve any changes to the system prompt
- Critical or sensitive responses flagged by users should be reviewed manually
- The system should not be deployed in a context where AI decisions have irreversible real-world consequences (e.g. financial transactions, medical decisions) without human review

---

## 6. Security Obligations

- The API key must **never** be committed to version control or shared publicly
- All production deployments must use HTTPS to encrypt data in transit
- Rate limiting must be enabled before public launch to prevent abuse
- Session access must be authenticated to prevent unauthorised access to conversation history

---

## 7. Compliance

This product must comply with:
- **GDPR / UK GDPR** — if deployed to users in the EU or UK
- **Google Gemini Terms of Service** — governing the use of the underlying AI model
- **EU AI Act (where applicable)** — as a general-purpose AI application

---

## 8. Policy Review

This policy should be reviewed and updated:
- Before any public production launch
- After any significant change to the AI model or data handling
- At minimum, every **6 months**

---

*Oghenetega EV Chatbot | Responsible AI Use Policy v1.0 | For educational use — Month 2 Weekly Project Assignment*
