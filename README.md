# ai-proxy
This is a python-based AI proxy.
It would be deployed in Railway as a gatekeeper of calling LLM models.

1. The api key would be managed centralized as railway variables so user do not need to have an llm api key to use the services.
2. It would expose the endpoint as the OpenAI API style, support the [Responses API](https://platform.openai.com/docs/api-reference/responses)
3. Add authentication to the proxy endpoint so only my app can call it
4. Optionally log/limit usage per user at the proxy layer
5. Optionally extend the procy to accept a user-provided key and forward it. By default using my api key.
