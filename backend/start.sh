#!/bin/bash
cd "$(dirname "$0")"  # 切换到脚本所在目录
export PYTHONPATH="$PYTHONPATH:$(dirname $(pwd))"  # 添加项目根目录到Python路径
python run.py 