import tiktoken


class TokenCounter:

    def __init__(self, model="gpt-4.1-mini"):
        """
        Initialize tokenizer for a specific model.
        """
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            # fallback if model encoding is not found
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """
        Count tokens in a single text string.
        """
        tokens = self.tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)

    def count_tokens_per_page(self, pages):
        """
        Count tokens for each page in a list of pages.
        """
        token_counts = []

        for page in pages:
            token_counts.append(self.count_tokens(page))

        return token_counts

    def get_token_statistics(self, pages):
        """
        Calculate min, avg, and max tokens from page list.
        """
        token_counts = self.count_tokens_per_page(pages)

        min_tokens = min(token_counts)
        avg_tokens = int(sum(token_counts) / len(token_counts))
        max_tokens = max(token_counts)

        return {
            "min": min_tokens,
            "avg": avg_tokens,
            "max": max_tokens
        }