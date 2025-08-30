import pandas as pd

from fnewscrawler.utils import deduplicate_text_df, deduplicate_chinese_texts


def test_deduplicate_text_df():
    df = pd.DataFrame({
        'content': ['这是重复的内容,kkk', '这是重复的内容', '这不是重复的内容']
    })
    df = deduplicate_text_df(df, 'content')
    print(df)
    assert len(df) == 2

def test_deduplicate_chinese_texts():
    texts = [
        "苹果发布了新款iPhone手机！",
        "苹果公司推出了最新的iPhone",
        "苹果发布新iPhone，性能更强",
        "谷歌发布了Pixel 8手机",
        "苹果 发布 了 新款 iPhone",
        "特斯拉发布了新款电动汽车",
        "苹果发布iPhone，搭载A17芯片"
    ]

    # 使用相似度去重（推荐）
    result = deduplicate_chinese_texts(
        texts,
        threshold=0.8  # 中文建议 0.5~0.7
    )

    print("去重结果：")
    for t in result:
        print(f"  • {t}")



if __name__ == '__main__':
    # test_deduplicate_chinese_texts()
    test_deduplicate_text_df()
