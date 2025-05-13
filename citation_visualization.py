import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import platform
import os

# 设置字体，解决中文显示问题
system = platform.system()
if system == 'Windows':
    # 尝试使用Windows系统自带的英文字体
    plt.rcParams['font.sans-serif'] = ['Arial', 'Calibri', 'sans-serif']
elif system == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial', 'sans-serif']
else:  # Linux和其他系统
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']

plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建有向图
G = nx.DiGraph()

# 添加我们的10篇主要论文作为节点（按照年份排序）
papers = {
    # 早期视觉密码学论文
    "Wu1998": {"title": "An image secret sharing method", "year": 1998},
    "Hou2003": {"title": "Visual cryptography for color images", "year": 2003},

    # 近期论文
    "Li2023": {"title": "Pragmatic Reasoning Unlocks Quantifier Semantics for Foundation Models", "year": 2023},
    "Chen2024": {
        "title": "Enhancing educational Q&A systems using a Chaotic Fuzzy Logic-Augmented large language model",
        "year": 2024},
    "Huang2024": {"title": "Large Language Models Based Fuzzing Techniques: A Survey", "year": 2024},
    "Kulugammana2024": {"title": "Are Large Language Models Good At Fuzzy Reasoning?", "year": 2024},
    "Li2024frog": {"title": "FRoG: Evaluating Fuzzy Reasoning of Generalized Quantifiers in Large Language Models",
                   "year": 2024},
    "Lin2024": {"title": "Let the Fuzzy Rule Speak: Enhancing In-context Learning Debiasing with Interpretability",
                "year": 2024},
    "Shoaip2024": {"title": "A dynamic fuzzy rule-based inference system using fuzzy inference with semantic reasoning",
                   "year": 2024},
    "Vertsel2024": {"title": "Hybrid LLM/Rule-based Approaches to Business Insights Generation from Structured Data",
                    "year": 2024},
}

# 添加被共同引用的关键论文
common_citations = {
    "Zadeh1965": {"title": "Fuzzy sets", "year": 1965},
    "Zadeh1973": {"title": "Outline of a new approach to the analysis of complex systems and decision processes",
                  "year": 1973},
    "Zadeh1975": {"title": "Fuzzy Logic and Approximate Reasoning", "year": 1975},
    "Devlin2019": {"title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                   "year": 2019},
    "Brown2020": {"title": "Language Models are Few-Shot Learners", "year": 2020},
}

# 添加所有节点
for paper_id, info in {**papers, **common_citations}.items():
    G.add_node(paper_id, **info)

# 添加论文之间的引用关系（基于搜索结果的推断）
# 格式: (被引用的论文, 引用论文) - 箭头方向从引用论文指向被引用论文
citations_between_papers = [
    ("Li2023", "Li2024frog"),  # Li2024frog引用了Li2023
    ("Li2023", "Lin2024"),  # Lin2024引用了Li2023
    ("Li2023", "Chen2024"),  # Chen2024引用了Li2023
    ("Li2023", "Kulugammana2024"),  # Kulugammana2024引用了Li2023
    ("Hou2003", "Shoaip2024"),  # Shoaip2024引用了Hou2003
    ("Li2023", "Huang2024"),  # Huang2024引用了Li2023
    ("Chen2024", "Vertsel2024"),  # Vertsel2024引用了Chen2024
    ("Lin2024", "Vertsel2024"),  # Vertsel2024引用了Lin2024
]

# 添加共同引用的关系
common_citations_relationships = {
    "Zadeh1965": ["Kulugammana2024", "Lin2024", "Chen2024", "Shoaip2024", "Li2024frog"],
    "Zadeh1975": ["Kulugammana2024", "Chen2024", "Shoaip2024", "Lin2024"],
    "Zadeh1973": ["Shoaip2024", "Chen2024", "Lin2024"],
    "Devlin2019": ["Li2023", "Li2024frog", "Kulugammana2024", "Lin2024"],
    "Brown2020": ["Li2023", "Kulugammana2024", "Li2024frog", "Chen2024", "Lin2024", "Vertsel2024"],
}

# 添加引用边 (被引用论文 <- 引用论文)
for cited, citing in citations_between_papers:
    G.add_edge(citing, cited, relation="cites")

# 添加共同引用边
for cited, citers in common_citations_relationships.items():
    for citer in citers:
        G.add_edge(citer, cited, relation="cites")

# 创建一个分层结构，最古老的论文在顶部，越新的论文越靠下
plt.figure(figsize=(16, 12))

# 计算每个节点的引用次数（被多少篇论文引用）
citation_count = {}
for node in G.nodes():
    citation_count[node] = sum(1 for _ in G.predecessors(node))

# 按年份和引用次数排序的论文列表
papers_by_year = {}
for node, data in {**papers, **common_citations}.items():
    year = data['year']
    if year not in papers_by_year:
        papers_by_year[year] = []
    papers_by_year[year].append((node, citation_count[node]))

# 排序年份（从旧到新）
sorted_years = sorted(papers_by_year.keys())

# 创建分层布局
pos = {}
layer_heights = {}
current_y = 0
layer_spacing = 2.0  # 层之间的垂直间距

# 为每个年份分配一个水平层
for year in sorted_years:
    papers_in_year = papers_by_year[year]
    # 按引用次数排序（被引用最多的在左边）
    papers_in_year.sort(key=lambda x: -x[1])  # 降序排序

    layer_heights[year] = current_y
    current_y -= layer_spacing

    # 水平分布同年发表的论文
    for i, (node, _) in enumerate(papers_in_year):
        # 将节点水平均匀分布
        x = i - (len(papers_in_year) - 1) / 2
        pos[node] = (x * 2, layer_heights[year])  # 乘以2增加水平间距

# 绘制节点
node_colors = []
node_sizes = []
for node in G.nodes():
    if node in papers:
        if G.nodes[node]['year'] < 2010:  # 较早的论文
            node_colors.append('lightcoral')
        else:  # 最近的论文
            node_colors.append('lightblue')
        node_sizes.append(1000 + citation_count[node] * 100)  # 被引用越多，节点越大
    else:  # 共同引用的论文
        node_colors.append('lightgreen')
        node_sizes.append(800 + citation_count[node] * 100)

# 绘制边
edge_colors = []
for u, v in G.edges():
    if u in papers and v in papers:
        edge_colors.append('blue')
    else:
        edge_colors.append('green')

# 绘制图形
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1.0, alpha=0.7,
                       arrows=True, arrowstyle='->', arrowsize=15)

# 绘制节点标签
labels = {}
for node in G.nodes():
    # 显示论文ID和年份
    year = G.nodes[node]['year']
    labels[node] = f"{node}\n({year})"

nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight='bold')

# 添加图例
plt.legend([
    plt.Line2D([0], [0], color='w', markerfacecolor='lightblue', marker='o', markersize=15),
    plt.Line2D([0], [0], color='w', markerfacecolor='lightcoral', marker='o', markersize=15),
    plt.Line2D([0], [0], color='w', markerfacecolor='lightgreen', marker='o', markersize=15),
    plt.Line2D([0], [0], color='blue', lw=2),
    plt.Line2D([0], [0], color='green', lw=2)
], [
    'Recent Papers (2020+)',
    'Early Papers (<2010)',
    'Commonly Cited Papers',
    'Citations Between Papers',
    'Citations to Classic Papers'
], loc='upper right')

plt.title('Fuzzy Logic and LLM Literature Citation Hierarchy', fontsize=20)
plt.axis('off')
plt.tight_layout()
plt.savefig('citation_hierarchy.png', dpi=300, bbox_inches='tight')
plt.close()

print("Citation hierarchy image generated: citation_hierarchy.png")