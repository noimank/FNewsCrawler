from typing import List
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from fnewscrawler.utils import get_project_root
# 全局缓存模型，避免重复加载
_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        # 中文通用轻量模型
        _MODEL = SentenceTransformer(os.path.join(get_project_root().absolute(), 'checkpoint/paraphrase-multilingual-MiniLM-L12-v2'))
    return _MODEL


def deduplicate_text_df(df: pd.DataFrame,
                        text_col: str,
                        threshold: float = 0.8) -> pd.DataFrame:
    """
    语义去重 DataFrame 指定列，返回去重后的 DataFrame（保留第一条）。

    参数
    ----
    df : pd.DataFrame
    text_col : str
        要去重的列名
    threshold : float
        语义相似度阈值（0~1）

    返回
    ----
    pd.DataFrame
        去重后的 DataFrame（索引重置）
    """
    if df.empty:
        return df

    texts = df[text_col].astype(str).tolist()
    model = _get_model()
    embs = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    clusters = util.community_detection(embs, threshold=threshold, min_community_size=2)
    keep_indices = set()
    for c in clusters:
        keep_indices.add(c[0])
    # 单篇未聚类也算保留
    keep_indices.update(set(range(len(texts))) - {i for c in clusters for i in c})

    return df.iloc[sorted(keep_indices)].reset_index(drop=True)


def deduplicate_chinese_texts(texts: List[str],
                              threshold: float = 0.8) -> List[str]:
    """
    语义去重中文新闻文本 list，返回去重后的 list（保留第一条）。

    参数
    ----
    texts : List[str]
    threshold : float

    返回
    ----
    List[str]
        去重后的文本列表
    """
    if not texts:
        return []

    model = _get_model()
    embs = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)

    clusters = util.community_detection(embs, threshold=threshold, min_community_size=2)
    keep_indices = set()
    for c in clusters:
        keep_indices.add(c[0])
    keep_indices.update(set(range(len(texts))) - {i for c in clusters for i in c})

    return [texts[i] for i in sorted(keep_indices)]
