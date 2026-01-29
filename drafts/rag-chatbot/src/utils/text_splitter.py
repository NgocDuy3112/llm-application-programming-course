class TextSplitter:
    def __init__(self, *, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._validate()


    def split(self, text: str) -> list[str]:
        if not text:
            return []

        normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        n = len(normalized)

        while start < n:
            end = min(start + self.chunk_size, n)
            if end < n:
                window = normalized[start:end]
                break_at = max(window.rfind("\n"), window.rfind(" "), window.rfind("\t"))
                if break_at > 0:
                    end = start + break_at

            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= n:
                break

            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = end
            start = next_start

        return chunks

    def _validate(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")



def split_text(text: str, *, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    return TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap).split(text)
