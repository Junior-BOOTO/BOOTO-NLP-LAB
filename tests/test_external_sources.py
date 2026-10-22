import pytest

from booto_nlp import external_sources


def test_pdf_import_rejects_non_pdf():
    with pytest.raises(ValueError, match="PDF valide"):
        external_sources.load_pdf(b"not a pdf")


def test_pdf_import_rejects_oversized_file():
    with pytest.raises(ValueError, match="5 Mo"):
        external_sources.load_pdf(b"%PDF" + b"x" * external_sources.MAX_PDF_BYTES)


def test_pdf_import_extracts_each_text_page_and_reports_progress(monkeypatch):
    class Page:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class Reader:
        is_encrypted = False
        pages = [Page(" Premier texte. "), Page(""), Page("Deuxième texte.")]

        def __init__(self, *_args, **_kwargs):
            pass

    monkeypatch.setattr(external_sources, "PdfReader", Reader)
    progress = []
    df = external_sources.load_pdf(
        b"%PDF test", "essai.pdf",
        progress_callback=lambda current, total: progress.append((current, total)),
    )
    assert df.text.tolist() == ["Premier texte.", "Deuxième texte."]
    assert df.page.tolist() == [1, 3]
    assert df.source.tolist() == ["essai.pdf", "essai.pdf"]
    assert progress == [(1, 3), (2, 3), (3, 3)]


def test_pdf_import_accepts_1000_pages(monkeypatch):
    class Page:
        def extract_text(self):
            return "Texte de la page."

    class Reader:
        is_encrypted = False
        pages = [Page() for _ in range(external_sources.MAX_PDF_PAGES)]

        def __init__(self, *_args, **_kwargs):
            pass

    monkeypatch.setattr(external_sources, "PdfReader", Reader)
    df = external_sources.load_pdf(b"%PDF test", "livre.pdf")
    assert len(df) == 1000
    assert df.page.iloc[-1] == 1000


def test_pdf_import_rejects_more_than_1000_pages(monkeypatch):
    class Page:
        def extract_text(self):
            return "Texte de la page."

    class Reader:
        is_encrypted = False
        pages = [Page() for _ in range(external_sources.MAX_PDF_PAGES + 1)]

        def __init__(self, *_args, **_kwargs):
            pass

    monkeypatch.setattr(external_sources, "PdfReader", Reader)
    with pytest.raises(ValueError, match="1000 pages"):
        external_sources.load_pdf(b"%PDF test", "livre.pdf")


def test_wikipedia_import_builds_cited_documents(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"query": {"pages": [{
                "pageid": 123,
                "title": "Intelligence artificielle",
                "extract": "Texte de l'article.",
            }]}}

    def fake_get(url, **kwargs):
        assert url == "https://fr.wikipedia.org/w/api.php"
        assert kwargs["params"]["gsrsearch"] == "IA"
        return Response()

    monkeypatch.setattr(external_sources.requests, "get", fake_get)
    df = external_sources.fetch_wikipedia(" IA ", "fr", 3)
    assert df.loc[0, "text"] == "Texte de l'article."
    assert df.loc[0, "source_url"].endswith("Intelligence_artificielle")
    assert df.loc[0, "license"].startswith("Wikipedia")


def test_wikipedia_import_validates_inputs():
    with pytest.raises(ValueError, match="Saisissez"):
        external_sources.fetch_wikipedia("   ")
    with pytest.raises(ValueError, match="langue"):
        external_sources.fetch_wikipedia("climat", "de")
