import os
from pathlib import Path
from typing import List

import pandas as pd
from huggingface_hub import snapshot_download
from sentence_transformers import SentenceTransformer, util

from fnewscrawler.utils import LOGGER


def download_sentence_transformer_model(
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    revision: str = "main",  # 可指定 commit hash / tag / branch
    cache_dir: str = None,
    only_required_files: bool = True
):
    """
    从 Hugging Face 镜像站下载 sentence-transformers 模型，支持指定版本和文件过滤。

    参数:
        model_name (str): 模型 ID
        revision (str): 模型版本（如 "main", "v1.0", 或 commit hash）
        cache_dir (str): 本地保存路径
        only_required_files (bool): 是否只下载推理必需文件
    """
    if cache_dir is None:
        home = Path.home()
        safe_model_name = model_name.replace("/", "_")
        cache_dir = home / "sentence-transformers" / safe_model_name

    cache_path = Path(cache_dir)

    # === 检查是否已存在核心文件 ===
    required_files = [
        "config.json",
        "modules.json",
        "tokenizer.json",
        "sentence_bert_config.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "config_sentence_transformers.json"
    ]
    # 检查是否存在权重文件（safetensors 优先）
    weight_exists = (cache_path / "model.safetensors").exists()
    config_exists = all((cache_path / f).exists() for f in required_files)

    if config_exists and weight_exists:
        LOGGER.info(f"新闻去重模型已存在，路径: {cache_path}，跳过下载。")
        return str(cache_path)

    LOGGER.info(f"正在下载模型 '{model_name}' (revision: {revision}) 到: {cache_path}")

    # 设置镜像站
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

    # === 文件过滤规则 ===
    if only_required_files:
        # 允许的文件模式（支持通配符）
        allow_patterns = [
            "*.json",               # 所有 JSON 配置
            "*.txt",                # 如 vocab.txt
            # "*.bin",                # PyTorch 权重
            "*.safetensors",        # SafeTensors 权重（优先）
            "1_Pooling/*.json",     # Pooling 层配置（sentence-transformers 特有）
            "2_Dense/*.bin",        # 部分模型可能有额外层
            "2_Dense/*.safetensors",
            "modules.json",
            "sentence_bert_config.json",
        ]
        # 明确排除的文件（避免下载数据集、日志等）
        ignore_patterns = [
            "*.md",
            "*.git*",
            "*tests*",
            "*examples*",
            "*logs*",
            "tf_model*",
            "unigram*",
            "pytorch_model.bin",
            "sentencepiece.bpe.model",
            "*onnx*",
            "*openvino*",
            "*training_args.bin",
            "*optimizer.pt",
            "*scheduler.pt",
            "*tokenizer.model",     # 如果使用 sentencepiece，可能需要保留，但此模型用 BERT tokenizer
        ]
    else:
        allow_patterns = None
        ignore_patterns = None

    try:
        snapshot_download(
            repo_id=model_name,
            revision=revision,
            local_dir=cache_path,
            force_download=True,
            token=False,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns
        )
        LOGGER.info(f"新闻去重模型下载完成，保存路径: {cache_path}")
        return str(cache_path)
    except Exception as e:
        LOGGER.error(f"新闻去重模型下载失败: {e}")
        if cache_path.exists():
            import shutil
            shutil.rmtree(cache_path)
        raise

# 全局缓存模型，避免重复加载
_MODEL = None

def _get_model(cache_dir=None):
    global _MODEL
    if cache_dir is None:
        home = Path.home()
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        safe_model_name = model_name.replace("/", "_")
        cache_dir = home / "sentence-transformers" / safe_model_name
    if _MODEL is None:
        # 中文通用轻量模型
        _MODEL = SentenceTransformer(str(cache_dir))
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
