# Exercise Flow — Overview and student-facing steps

Flow: LLM -> System Prompt -> Temperature & Max tokens -> Sliding Window -> Function Calling -> Aggregate (E2E)

This document replaces scattered "TODO" markers with a clear, ordered flow students should implement and verify. Each numbered step below describes the goal, the files to update, and the acceptance criteria.

1) LLM adapter (core integration)
- Files: `exercises/model/adapter.py`
- Goal: Implement the adapter's `response` method so it builds provider parameters and calls the provider's chat API.
- Key points:
  - Convert `ToolChoice` (enum) into the provider's function-calling argument format.
  - Map `tools` → provider `functions` (OpenAI-compatible) when function calling is enabled.
  - Include `model`, `messages`, `temperature`, `max_tokens` and any passthrough kwargs.
- Acceptance: `MockAdapter` remains available for local testing; `GroqAdapter`/`OllamaAdapter` should construct a client and not crash if env vars missing (raise clear errors).

2) System prompt and message construction
- Files: `exercises/orchestrator/engine.py`
- Goal: Ensure `instruction` is converted into a `system` message and included as the first message sent to the LLM.
- Key points:
  - Sanitize memory entries before sending (keep role/content; include `tool_call_id` and `name` for `tool` messages).
  - Ensure the most recent user message aligns with any preprocessing applied.
- Acceptance: When `instruction` is provided, adapter receives a leading `system` message with that content.

3) Temperature & max_tokens (model config)
- Files: `exercises/ui/sidebar.py`, `exercises/app.py`, `exercises/orchestrator/engine.py`, `exercises/model/adapter.py`
- Goal: Wire the UI controls through the engine into the adapter call.
- Key points:
  - Sidebar exposes `temperature` and `max_tokens` (already present).
  - `engine.response` must accept and forward these values to `adapter.response`.
  - Adapter must include these in the provider parameters when calling the chat API.
- Acceptance: Changing the UI values changes parameters passed into `adapter.response` (verifiable with `MockAdapter`).

4) Sliding window memory
- File: `exercises/orchestrator/memory.py`
- Goal: Make sure `WindowMemory` returns the correct recent slice and that `add`/`add_tool_message` produce provider-ready shapes.
- Key points:
  - `WindowMemory.get_messages()` returns at most `2 * sliding_window_size` messages (pairs of user/assistant).
  - Tool messages include `tool_call_id` and `name` so the model can relate outputs to calls.
- Acceptance: Unit test verifies buffer trimming and message shapes (see existing tests in `tests/`).

5) Function calling (tools)
- Files: `exercises/orchestrator/engine.py`, `exercises/orchestrator/tools.py`
- Goal: Implement the tool-calling loop in the engine and at least one working tool stub.
- Key points:
  - Detect `tool_calls` on assistant messages from the model response.
  - Parse tool arguments robustly (string → JSON, dict → use directly).
  - Lookup `AVAILABLE_FUNCTIONS` by tool name and invoke with parsed args.
  - Save tool outputs using `memory.add_tool_message(...)` so the next model call can see results.
  - Repeat until the model returns a final assistant message without `tool_calls`.
- Acceptance: Engine can handle a tool request end-to-end using `tavily_search` (mocked) or a simple test function.

6) Aggregate / end-to-end
- Files: all of the above plus `tests/run_tests.py`
- Goal: Provide a minimal E2E example and student checklist so the app can be run with `MockAdapter` when API keys are absent.
- Key points:
  - Include a short "how to run" in `exercises/README.md` or the top-level README.
  - Provide sample `.env.example` showing required env vars (GROQ_API_KEY, TAVILY_API_KEY).
- Acceptance: Students can run tests locally against `MockAdapter` and, optionally, run the Streamlit demo with real credentials.

Notes / Tips
- Recommend students implement the adapter and `MockAdapter` first and verify behavior using unit tests.
- Advanced features (streaming, retry/backoff, separate reasoning content) should be introduced as optional extras after the E2E flow is working.

If you'd like, I can now:
- replace `exercises/EXERCISE_TODOs.md` with this flow text (done),
- remove any remaining `TODO` comments in the exercises (already cleaned), or
- generate a compact student-facing checklist (markdown) to include in the repo root.
