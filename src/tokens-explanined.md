NOTE: Use custom token counting to count tokens whenever this occurs, instead of using OpenAI's token counting from the API responses

Initialize total_processed_tokens = 0 # this aims to represent the total number of tokens processed by AI (chat and query expansion) throughout the session

Initialize total_conversation_tokens = 0 # this aims to represent the total number of tokens in the cleaned conversation history (the chatbot system prompt, cleaned chat user content, and assistant (response) content) throughout the session -- effectively the same as the above, without RAG context tokens

Initialize total_rag_context_tokens = 0 # this aims to represent the total number of tokens in the RAG context (the RAG chunks) throughout the session


user submits chat query
- not counted. do no counting with this right now.

concatenate entire CLEANED conversation history of "user" + "assistant" chat messages + current user query + insert all of this into the query expansion prompt
- count the tokens of this full prompt and increment total processed tokens with this value

RAG retrieval returns k chunks
- increment total_rag_context_tokens with the number of tokens in the returned (post-deduplication) RAG chunks

Set temp variable to store user query by itself (without any other information)

Concatenate all chunks + original user query + entire CLEANED conversation history to create chat prompt input
- count these tokens and increment total processed tokens with this value

Chat response is streamed. Wait until the entire response has finished streaming.
- count the response tokens and increment total processed tokens with this value

Use the temp variable contents to overwrite the most recent chat 'user' message (effectively removing the RAG context from the chat history, leaving only the messages between the user and the assistant)

Update the token conversation tokens with the cleaned conversation chat history (without the RAG context). Be sure to not exclude the system message.


---

Maintain the following token counts in the sidebar:
- "Total Processed Tokens" = total_processed_tokens
- "Total Conversation Tokens" = total_conversation_tokens
- "Total Document Context Tokens" = total_rag_context_tokens
- "Total Input Tokens" -> you'll need to track specifically all input tokens from each finalized query expansion prompt and concatendated user chat prompt (concatenated with all other context)
- "Total Output Tokens" -> you'll need to track specifically all output tokens from each chat response, and each query expansion response
- "Estimated Session Price" = total input tokens * input token price + total output tokens * output token price

