from unittest.mock import MagicMock, patch


def test_embed_texts_returns_vectors():
    mock_model = MagicMock()
    import numpy as np

    mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384])

    with patch("app.pipeline.embedder.get_embedder", return_value=mock_model):
        from app.pipeline.embedder import embed_texts

        vectors = embed_texts(["hello", "world"])

    assert len(vectors) == 2
    assert len(vectors[0]) == 384


def test_embed_query_returns_single_vector():
    mock_model = MagicMock()
    import numpy as np

    mock_model.encode.return_value = np.array([[0.5] * 384])

    with patch("app.pipeline.embedder.get_embedder", return_value=mock_model):
        from app.pipeline.embedder import embed_query

        vec = embed_query("test question")

    assert len(vec) == 384
