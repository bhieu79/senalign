from src.article.ArticleFactory import LAOS_LANGID
from src.article.EmbeddableArticle import EmbeddableArticle


class LaosArticle(EmbeddableArticle):
    sentence_separator = r"(?<!\w[\.៕។]\w[\.៕។])(?<![A-Z][a-z][\.៕។])(?<=[\.៕។]|\?|\!)\s"

    def __init__(self):
        super().__init__(LAOS_LANGID)