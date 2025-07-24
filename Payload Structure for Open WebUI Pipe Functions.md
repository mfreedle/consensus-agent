<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Payload Structure for Open WebUI Pipe Functions

Open WebUI Pipe functions are designed to process custom logic and route data, often acting as bridges to external APIs, LLMs, or workflow automation tools. When Open WebUI invokes a Pipe function, it passes a payload with clearly defined structure and expectations.

## Core Payload Format

A typical payload passed to a Pipe function is a Python dictionary (parsed from JSON) with the following fields:


| Field | Type | Description |
| :-- | :-- | :-- |
| `model` | string | The model or identifier selected by the user. |
| `messages` | list of objects | Chat history, each message as a dict with `role` and `content`. |
| `stream` | boolean | Whether the response should be streamed. |
| Additional fields | varies | May contain other inference parameters (temperature, token limit, etc.). |

#### Example Minimal Payload

```python
{
  "model": "archive",
  "messages": [
    {"role": "user", "content": "Please analyze this file"}
  ],
  "stream": False
}
```

This matches what is typically observed within custom Pipe implementations and debugging workflows[^1_1][^1_2].

## Working with the Payload

- The function `pipe(self, body: dict, __user__: dict)` (or similar) is the main entry point.
- `body` contains the payload as described above.
- For most scenarios, you extract the latest user message or process the `messages` list as needed.

**Note:** If you expect file data or uploads, current community feedback indicates the default payload does not include file metadata or URLs within `messages` or as top-level fields (despite a successful upload in the UI)[^1_1]. Custom handling or additional integration may be required for accessing uploaded file information, depending on your Open WebUI deployment.

## Configuration and Parameters

Many Pipes reference configurable options ("Valves"), declared in a nested class, and use values such as API keys, endpoints, and option flags[^1_3][^1_2]. These are not part of the runtime payload but configured when the pipe is instantiated.

## Usage Pattern

A typical Pipe function workflow:

1. Extract user input or relevant data from `body['messages']`.
2. Prepare a request payload for your backend or API, possibly adding options from Valves.
3. Send the request and handle the response.
4. Format and return the result in a shape Open WebUI recognizes (often an LLM-style completion or a dict with a message).

## Payload Edge Cases

- **Streaming:** If `stream` is `True`, the Pipe may return an iterable/generator for chunked response[^1_3].
- **Error Handling:** Return a dict or message string on errors; Open WebUI will display this directly.
- **Advanced parameters:** The payload might include fields like `temperature`, `max_tokens`, etc., passed through to your backend as needed.


## Summary Table

| Parameter | Mandatory | Example Value | Notes |
| :-- | :-- | :-- | :-- |
| `model` | Yes | `"gpt-3.5-turbo"` | LLM or custom model identifier |
| `messages` | Yes | `[{"role": "user", ...}]` | Full chat context |
| `stream` | No | `true` | If streaming output is needed |
| (custom fields) | Optional | `temperature`, `file_url`, etc. | If supported by your logic/backends |

## References

- Pipe structure and usage pattern[^1_3][^1_4][^1_2]
- Community workflow code and file upload caveats[^1_1]
- General best practices from plugin documentation[^1_3][^1_4][^1_2]

<div style="text-align: center">⁂</div>

[^1_1]: https://community.n8n.io/t/question-how-to-access-uploaded-file-e-g-markdown-in-custom-openwebui-pipe-for-n8n-integration/149104

[^1_2]: https://www.pondhouse-data.com/blog/integrating-n8n-with-open-webui

[^1_3]: https://docs.openwebui.com/features/plugin/functions/pipe/

[^1_4]: https://docs.openwebui.com/pipelines/pipes/

[^1_5]: https://github.com/open-webui/open-webui/discussions/10565

[^1_6]: https://www.reddit.com/r/OpenWebUI/comments/1ivh81v/finally_figured_it_out_openweb_ui_with_your_own/

[^1_7]: https://www.youtube.com/watch?v=oNXqLWeWhYY

[^1_8]: https://ai.stackexchange.com/questions/48350/connect-open-webui-with-langflow-using-open-webui-function-pipe

[^1_9]: https://ikasten.io/2024/06/03/getting-started-with-openwebui-pipelines/

[^1_10]: https://docs.openwebui.com/features/


---

# What response format is Open WebUI expecting back from the Pipe Function?

Open WebUI expects the **response from a Pipe Function** to be one of the following formats, depending on your desired outcome and user experience:

## 1. **A Simple String**

If you return a plain string, Open WebUI will display this string as the response to the user.

```python
def pipe(self, body: dict):
    return "Hello, World!"
```

*This is sufficient for simple, text-only outputs and is often used for basic or prototyping Pipes.*
[^2_1][^2_5]

## 2. **A Dictionary Mimicking LLM Responses**

For more advanced integrations (such as connecting to LLM APIs, RAG workflows, or returning structured data), it is best practice to return a dictionary following the OpenAI/Chat completion schema, typically with keys like `content`, `role`, and possibly usage metadata.

**Example:**

```python
def pipe(self, body: dict):
    return {
        "role": "assistant",
        "content": "Here is your answer.",
        # Optionally add more fields if needed:
        # "usage": {"completion_tokens": 42, ...}
    }
```

This format enables richer UI rendering and compatibility with many built-in and custom workflows, as seen in the [DeepSeek, Google Gen AI, and Anthropic integrations][^2_3].

## 3. **A Generator or Iterator for Streaming Responses**

If your Pipe should provide a streaming, multi-part response, you can return a generator or iterator yielding either strings or dictionaries as above. Open WebUI will stream each chunk incrementally to the UI.

**Example:**

```python
def pipe(self, body: dict):
    yield {"role": "assistant", "content": "Processing..."}
    yield {"role": "assistant", "content": "Step 1 complete."}
```

*Streaming is useful for long-running tasks or integrations with LLMs that support streaming output.*
[^2_5]

## Key Points

- **Minimal response**: a string is okay for basic returns[^2_1][^2_5].
- **Best practice**: return a dict with at least a `role` and `content` field for LLM-like user experiences[^2_3][^2_5].
- **Streaming**: use a generator if you want progressive responses or need to support streaming in the UI[^2_5].
- **Additional fields**: you may add metadata (such as token usage, function call info, etc.) if relevant. Open WebUI will ignore unknown fields but may use recognized ones for enhanced UX[^2_3].
- **No enforced schema**: There’s no *strictly* enforced schema, but following the OpenAI-like structure maximizes compatibility with the chat interface and downstream tools[^2_3][^2_5].

**In summary:**
Open WebUI expects Pipe Function responses to be either a plain string, a dictionary (mimicking OpenAI's chat completion format), or a generator yielding such outputs. For the best integration, use a dict with `content` and `role` fields[^2_1][^2_3][^2_5].

<div style="text-align: center">⁂</div>

[^2_1]: https://docs.openwebui.com/features/plugin/functions/pipe/

[^2_2]: https://docs.openwebui.com/features/plugin/functions/

[^2_3]: https://www.youtube.com/watch?v=oNXqLWeWhYY

[^2_4]: https://www.reddit.com/r/OpenWebUI/comments/1ky43wb/i_am_new_to_open_webui_i_wanted_to_know_what_is/

[^2_5]: https://zohaib.me/extending-openwebui-using-pipelines/

[^2_6]: https://docs.openwebui.com/pipelines/pipes/

[^2_7]: https://docs.openwebui.com/pipelines/functions/

[^2_8]: https://ikasten.io/2024/06/03/getting-started-with-openwebui-pipelines/

[^2_9]: https://github.com/open-webui/open-webui/discussions/8955

[^2_10]: https://github.com/open-webui/open-webui/discussions/3134

