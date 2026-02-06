
import sys
from pathlib import Path

# 定义唯一项目根目录名
ROOT_DIR_NAME = "klee-graph"
# 1. 获取当前脚本的路径对象（pathlib核心，面向对象）
# Path(__file__)：当前脚本路径（支持相对/软链接）
# resolve()：转为绝对路径+解析软链接，等价于os.path.abspath+os.path.realpath
script_path = Path(__file__).resolve()

# 2. 向上遍历路径，查找项目根目录（pathlib的parent属性实现向上找父目录）
# 从脚本所在目录开始，逐层向上找，直到系统根目录
current_dir = script_path.parent
project_root = None
while True:
    # 判断当前目录名是否为目标根目录（pathlib的name属性=目录/文件名）
    if current_dir.name == ROOT_DIR_NAME:
        project_root = current_dir
        break
    # 终止条件：到达系统根目录（parent等于自身，无法再向上）
    current_dir = current_dir.parent


# 3. 校验是否找到根目录，未找到则抛异常
if not project_root:
    raise FileNotFoundError(
        f"未找到项目根目录「{ROOT_DIR_NAME}」，请检查目录名称或脚本所在位置"
    )

# 4. 插入sys.path（pathlib对象可直接转字符串，兼容sys.path）
sys.path.insert(0, str(project_root))

# 验证（可选）
print(f"项目根目录：{project_root}")
print(f"sys.path最高优先级：{sys.path[0]}")