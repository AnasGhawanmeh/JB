from core.chunker import batch_units, split_text, split_with_offsets


def test_short_text_is_one_chunk():
    assert split_text("Hello world.", 100) == ["Hello world."]


def test_split_is_lossless_and_bounded():
    text = ("This is a sentence about emissions. " * 40 + "\n") * 30
    chunks = split_text(text, 500)
    assert "".join(chunks) == text
    assert all(len(c) <= 500 for c in chunks)


def test_long_paragraph_splits_on_sentences():
    text = "First sentence here. Second sentence here. Third sentence here."
    chunks = split_text(text, 45)
    assert "".join(chunks) == text
    assert chunks[0].endswith("here. ")


def test_word_and_hard_splits():
    words = "word " * 50
    assert all(len(c) <= 23 for c in split_text(words, 23))
    assert "".join(split_text("x" * 100, 30)) == "x" * 100


def test_offsets_match_text():
    text = "Alpha beta. " * 100
    for offset, piece in split_with_offsets(text, 70):
        assert text[offset:offset + len(piece)] == piece


def test_batches_map_back_to_units():
    texts = ["First paragraph.", "", "Second paragraph has more words.", "Third."]
    batches = batch_units(texts, max_chars=40)
    assert all(len(b.text) <= 40 for b in batches)
    for batch in batches:
        for seg in batch.segments:
            piece = batch.text[seg.batch_offset:seg.batch_offset + seg.length]
            assert texts[seg.unit_index][seg.unit_offset:seg.unit_offset + seg.length] == piece
    # a range inside the separator does not map to any unit
    first = batches[0]
    if len(first.segments) > 1:
        gap = first.segments[0].length
        assert first.locate(gap, gap + 2) is None


def test_long_unit_is_split_across_batches():
    texts = ["Sentence number one is here. " * 10]
    batches = batch_units(texts, max_chars=100)
    assert len(batches) > 1
    rebuilt = "".join(b.text for b in batches)
    assert rebuilt == texts[0]
