# I built an agent that closes deals, here’s what I learned.

I’ve always been skeptical of the “AI agent” hype. Too often, I see demos of stateless chatbots that act like glorified encyclopedias. They answer questions, they generate text, but they don't actually *work* alongside you. They don't remember what you told them five minutes ago, let alone five days ago.

As an engineer, I wanted to build something that felt less like a party trick and more like a colleague. I set out to build an AI Deal Intelligence Agent—something that could sit in the background of a B2B sales cycle, digest call notes, remember client objections, and draft highly contextual follow-ups.

I quickly realized that the hardest part of building a useful agent isn't the LLM. It's the memory. In this post, I'll walk you through how I designed "SalesMind," why I threw out my initial RAG architecture, and how integrating [Vectorize agent memory](https://vectorize.io/what-is-agent-memory) fundamentally changed the way the system operates.

## The Problem with Amnesiac AI

My initial prototype was simple. I hooked up a modern LLM to a chat interface. A sales rep could say, "Draft a follow up email to Stark Industries." The LLM would spit out a generic, polite, completely useless email. 

To make it useful, the rep had to explicitly provide the context *every single time*: "Draft a follow up email to Stark Industries. Remember they were worried about implementation time, they use AWS, and I like my emails under 100 words."

This isn't an assistant; it's a compiler that requires overly verbose syntax. If a human sales assistant forgot a client's main objection between Monday and Thursday, they would be fired. Why do we accept it from AI?

I needed a persistent memory layer.

## Architecture: Moving from RAG to Native Memory

My first instinct was to build a standard Retrieval-Augmented Generation (RAG) pipeline. I set up a vector database, chunked my call notes, embedded them, and performed cosine similarity searches before every LLM call.

It was... okay. But it was brittle. RAG is great for querying static documentation ("What is our refund policy?"), but it struggles with dynamic, evolving conversational context. When a user says "Forget what I said earlier, they actually use Azure," a naive vector search might still retrieve the older "AWS" note because it's semantically similar, confusing the LLM.

I needed a system designed specifically for *agentic memory*. That's when I ripped out my vector DB and integrated Hindsight. You can check out the [Hindsight GitHub](https://github.com/vectorize-io/hindsight) for the technical specs, but essentially, it acts as a dedicated memory plane. It doesn't just do dumb vector search; it manages the lifecycle of context.

Here is what the architecture looks like now:

1. **Frontend**: A clean, glassmorphism-styled UI built with Vanilla JS. It features a split-pane design so the user can literally see the memory log and the context being recalled in real-time.
2. **Backend**: FastAPI (Python) handling the orchestration.
3. **Memory Layer**: Hindsight managing session-based persistent memory (called via REST API).
4. **LLM Engine**: An LLM processing the prompt + recalled context.

[INSERT ARCHITECTURE DIAGRAM HERE]

## The Code: How Memory Actually Works

Let's look at the implementation. In my FastAPI backend, I created a `MemoryAgent` class. The beautiful thing about using a dedicated memory system is how clean the orchestration code becomes.

```python
import requests

class MemoryAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hindsight.vectorize.io"

    def store_memory(self, session_id: str, content: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"session_id": session_id, "text": content}
        requests.post(f"{self.base_url}/v1/memory", json=payload, headers=headers)
        return True

    def recall_memory(self, session_id: str, query: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"session_id": session_id, "query": query}
        res = requests.post(f"{self.base_url}/v1/memory/search", json=payload, headers=headers)
        return [r.get("text") for r in res.json().get("results", [])]
```

When a user sends a message, the flow is strictly ordered: Recall -> Generate -> Store.

```python
def generate_response(self, session_id: str, user_input: str):
    # 1. Recall relevant memory based on the new input
    recalled_context = self.recall_memory(session_id, user_input)
    
    # 2. (LLM Generation happens here, injecting recalled_context into the system prompt)
    response_text = self.llm.generate(prompt=user_input, context=recalled_context)
    
    # 3. Store the new input so the agent learns from this interaction
    self.store_memory(session_id, user_input)
    
    return response_text
```

If you want to dive deeper into the API, the [Hindsight docs](https://hindsight.vectorize.io/) cover the nuanced parameters you can tweak for recall decay and relevance.

## The Result: A Concrete Example

The difference in the UX is night and day. Here is a real interaction flow from the completed system.

[INSERT SCREENSHOT OF UI WITHOUT MEMORY HERE]

**Interaction 1: Feeding the Memory**
*User*: "Just got off the intro call with Stark Industries. They are highly interested but explicitly worried about our implementation time dragging out. Also, note for the future: I prefer my emails to be short and punchy."
*Agent*: "Got it. I've stored their concern about implementation time and your preference for short emails."

[INSERT SCREENSHOT OF UI WITH RECALLED CONTEXT VISIBLE HERE]

**Interaction 2: The Payoff (Days Later)**
*User*: "Draft a follow up email to Stark Industries."
*Agent (Recalling Memory...)*: 
> "Hi Tony, following up on our call. Our AWS integration deploys in under 24 hours, directly addressing your implementation timeline concerns. Let's sync with procurement. -Alex"

Without memory, the agent would have drafted a 4-paragraph generic marketing email. With memory, it hit the specific objection (implementation time) and adopted the user's stylistic preference (short and punchy) automatically.

## Lessons Learned

Building this taught me a few hard truths about the current state of AI engineering:

1. **Visibility builds trust.** Initially, I hid the memory recall process in the backend logs. Users didn't trust the agent because they didn't know *why* it was saying certain things. Once I exposed a "Recalled Context" panel in the UI, user confidence skyrocketed. They could see the agent "thinking."
2. **RAG is not Memory.** Standard document retrieval is fundamentally different from conversational memory. Managing state, overriding old facts with new facts, and weighting recent user preferences requires specialized tooling. Don't try to build this from scratch with a raw vector database unless you have months to burn.
3. **Latency matters.** When you add a memory recall step *before* the LLM generation step, you are adding latency. You must optimize your memory search to return in milliseconds, otherwise the chat experience feels sluggish. 

Persistent memory is what transitions an LLM from a cool tech demo into a piece of foundational business software. The agents of tomorrow won't just be smart; they will remember. And that makes all the difference.
